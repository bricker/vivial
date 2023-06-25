resource "google_secret_manager_secret" "all" {
  for_each = toset([
    "EAVE_DB_HOST",
    "EAVE_DB_USER",
    "EAVE_DB_PASS",
    "EAVE_DB_NAME"
  ])

  secret_id   = each.key
  expire_time = null
  labels      = {}
  ttl         = null
  replication {
    automatic = true
  }
}
