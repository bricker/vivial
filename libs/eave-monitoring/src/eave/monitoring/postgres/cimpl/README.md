# PostgreSQL Database atom collector

Uses the LISTEN/TRIGGER API in PostgreSQL to receive notifications on any INSERT, UPDATE, or CREATE operations.
It then constructs a raw atom payload, and sends it via HTTPS to the Eave backend for further processing.

## Dev setup

### Requirements

## TODO:

probs want some pre-processing to make sure we dont send sensitive info to eave backend (if possible)
