resource "google_sql_database" "app" {
  name            = "eave"
  instance        = data.google_sql_database_instance.given.name
  deletion_policy = "ABANDON"
}

resource "google_sql_user" "app" {
  instance        = data.google_sql_database_instance.given.name
  name            = trimsuffix(data.google_service_account.app_service_account.email, ".gserviceaccount.com")
  type            = "CLOUD_IAM_SERVICE_ACCOUNT"
  password        = null # only IAM supported
  deletion_policy = "ABANDON"
}
