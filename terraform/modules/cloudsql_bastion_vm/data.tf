data "google_service_account" "target_service_account" {
  account_id = var.target_service_account_id
}

data "google_iam_role" "compute_oslogin_role" {
  name = var.compute_oslogin_role_name
}

data "google_iam_role" "service_account_user_role" {
  name = var.service_account_user_role_name
}