resource "google_sql_database" "app" {
  lifecycle {
    prevent_destroy = true
  }

  name            = "eave"
  instance        = var.google_sql_database_instance.name
  deletion_policy = "ABANDON"
}

resource "google_sql_user" "app" {
  lifecycle {
    prevent_destroy = true
  }

  instance        = var.google_sql_database_instance.name
  name            = trimsuffix(module.service_accounts.google_service_account.email, ".gserviceaccount.com")
  type            = "CLOUD_IAM_SERVICE_ACCOUNT"
  password        = null # only IAM supported
  deletion_policy = "ABANDON"
}
