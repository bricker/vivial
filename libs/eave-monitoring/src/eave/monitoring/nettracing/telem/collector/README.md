# OpenTelemetry collectors

OpenTelemetry has a helper tool `ocb` that can be used to generate Golang code for simple, starter collector setups.
I've run the command `ocb --config builder-config.yaml` with the files here to generate the boilerplate code in the `eave/` directory.

NOTE: Requires a Golang 1.20.x toolchain to generate and build the project code from scratch.

Tutorial: https://opentelemetry.io/docs/collector/custom-collector/
