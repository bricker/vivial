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
