resource "google_sql_database" "app" {
  lifecycle {
    prevent_destroy = true
  }

  name            = "eave"
  instance        = data.google_sql_database_instance.given.name
  deletion_policy = "ABANDON"
}

resource "google_sql_user" "app" {
  lifecycle {
    prevent_destroy = true
  }

  instance        = data.google_sql_database_instance.given.name
  name            = trimsuffix(data.google_service_account.app_service_account.email, ".gserviceaccount.com")
  type            = "CLOUD_IAM_SERVICE_ACCOUNT"
  password        = null # only IAM supported
  deletion_policy = "ABANDON"
}
