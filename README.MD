# Polyxiety
A tool to monitor checkpoints on the Polygon network, and provide prometheus metrics relevant to a validator signing/missing checkpoints

## Usage
Make a config file in src/config.json something like:
```json
{
  "validator_address": "0x9eaD03F7136Fc6b4bDb0780B00a1c14aE5A8B6d0",
  "validator_name": "Luganodes"
}
```
The repository comes with a service file

## Metrics
- See metrics
```
curl localhost:8000/metrics
```

- HELP missed_last_checkpoint Indicates if a specific validator missed a checkpoint (1 for missed, 0 for not missed)
- TYPE missed_last_checkpoint gauge
```
missed_last_checkpoint{validator_address="YOUR VALIDATOR ADDRESS""} 0.0
```
- HELP missed_checkpoint_in_last_5 Indicates if a specific validator missed a checkpoint (1 for missed, 0 for not missed)
- TYPE missed_checkpoint_in_last_5 gauge
```
missed_checkpoint_in_last_5{validator_address="YOUR VALIDATOR ADDRESS"} 0.0
```
