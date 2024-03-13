#!/usr/bin/env bash

set -eu

# keydir=$(dirname "$TARGET_KEY")
# fname=$(basename "$TARGET_KEY")
# derout="$keydir/$fname.der"

# Convert PEM to DER
# https://cloud.google.com/kms/docs/formatting-keys-for-import
# openssl pkcs8 -topk8 -nocrypt -inform PEM -outform DER \
# 	-in "${TARGET_KEY}" \
# 	-out "$derout"

openssl pkeyutl \
  -encrypt \
  -pubin \
  -inkey ${PUB_WRAPPING_KEY} \
  -in ${TARGET_KEY} \
  -out ${WRAPPED_KEY} \
  -pkeyopt rsa_padding_mode:oaep \
  -pkeyopt rsa_oaep_md:sha256 \
  -pkeyopt rsa_mgf1_md:sha256

gcloud kms keys versions import \
	--import-job metabase_jwt_key_import \
	--location global \
	--keyring primary \
	--key metabase-jwt-key \
	--algorithm rsa-decrypt-oaep-4096-sha256 \
	--target-key-file "$WRAPPED_KEY"
