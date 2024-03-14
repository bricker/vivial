#!/usr/bin/env bash

set -eu

keydir=$(dirname "$TARGET_KEY")
fname=$(basename "$TARGET_KEY")
derout="$keydir/$fname.der"

# Convert PEM to DER
# https://cloud.google.com/kms/docs/formatting-keys-for-import
openssl pkcs8 -topk8 -nocrypt -inform PEM -outform DER \
	-in "${TARGET_KEY}" \
	-out "$derout"

gcloud kms keys versions import \
	--import-job eave_github_private_key_import \
	--location global \
	--keyring primary \
	--key eave-github-app-signing-key-01 \
	--algorithm rsa-sign-pkcs1-2048-sha256 \
	--target-key-file "$derout"
