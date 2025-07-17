import requests
import time
from prometheus_client import start_http_server, Gauge
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
TICK = "✅"
CROSS = "❌"
# --- Configuration ---
# Replace with your validator's address
with open("config.json") as f:
    config = json.load(f)

VALIDATOR_ADDRESS =  config["validator_address"]
VALIDATOR_NAME = config["validator_name"]
# The API endpoint that provides missing signer information
API_URL = "https://validator.info/api/polygon/blockchain/last-checkpoints"
# The port for the Prometheus metrics server
METRICS_PORT = 8000
LOG_FILE_NAME="polyxiety.log.json"

# --- Prometheus Gauge ---
missed_last_checkpoint_gauge = Gauge(
    'missed_last_checkpoint',
    'Indicates if a specific validator missed a checkpoint (1 for missed, 0 for not missed)',
    ['validator_address']
)

missed_checkpoint_in_last_5_gauge = Gauge(
    'missed_checkpoint_in_last_5',
    'Indicates if a specific validator missed a checkpoint (1 for missed, 0 for not missed)',
    ['validator_address']
)

def check_for_missed_checkpoints(latest_known_checkpoint):
    """
    Fetches the list of validators that missed the last checkpoint
    and updates the Prometheus gauge.
    """
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        with open(f"{LOG_FILE_NAME}", 'w') as f:
            json.dump(data, f, indent=2)

        checkpoint_data = []
        for validator in data:
            if validator["validatorName"] == VALIDATOR_NAME:
                checkpoint_data = validator["values"][:50]
                break
        if checkpoint_data[0]["value"] > latest_known_checkpoint:
            latest_known_checkpoint = checkpoint_data[0]["value"]
            missed_last_checkpoint_gauge.labels(validator_address=VALIDATOR_ADDRESS).set(0)
            missed_checkpoint_in_last_5_gauge.labels(validator_address=VALIDATOR_ADDRESS).set(0)
            for checkpoint in checkpoint_data:
                checkpoint_number = checkpoint["value"]
                index = checkpoint_data.index(checkpoint)
                if checkpoint["isSigned"] == False:
                    if index == 0:
                        missed_last_checkpoint_gauge.labels(validator_address=VALIDATOR_ADDRESS).set(1)
                        logging.info(f"{CROSS} Checkpoint {checkpoint_number} was missed by {VALIDATOR_ADDRESS}")
                    elif index < 5:
                        missed_checkpoint_in_last_5_gauge.labels(validator_address=VALIDATOR_ADDRESS).set(1)
                else:
                    if index == 0:
                        logging.info(f"{TICK} Checkpoint {checkpoint_number} was signed by {VALIDATOR_ADDRESS}")
    except Exception as e:
        logging.error(f"Error has occured: {e}")
    return latest_known_checkpoint

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(METRICS_PORT)
    print(f"Prometheus metrics server started on port {METRICS_PORT}")

    # Run the check periodically.
    latest_known_checkpoint = 0
    while True:
        latest_known_checkpoint = check_for_missed_checkpoints(latest_known_checkpoint)
        time.sleep(10) # Check every 5 minutes
