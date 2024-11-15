resource "google_kms_key_ring" "primary" {
  name     = "primary"
  location = "global"
}

resource "google_kms_crypto_key" "jws_signing_key" {
  name            = "jws-signing-key"
  key_ring        = google_kms_key_ring.primary.id
  purpose = "MAC"

  version_template {
    protection_level = "SOFTWARE"
    algorithm = "HMAC_SHA256"
  }

  lifecycle {
    prevent_destroy = true
  }
}

locals {
  jws_signing_key_version_count = 1
}

resource "google_kms_crypto_key_version" "jws_signing_key_versions" {
  count = local.jws_signing_key_version_count
  crypto_key = google_kms_crypto_key.jws_signing_key.id
}

# resource "google_kms_crypto_key_iam_binding" "jws_signing_key_iam_binding" {
#   crypto_key_id = google_kms_crypto_key.jws_signing_key.id
#   role          = "roles/cloudkms.cryptoKeyEncrypter"
#   members = var.jws_signing_key_accessors
# }
