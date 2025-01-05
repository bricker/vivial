data "google_iam_role" "compute_oslogin_role" {
  name = var.compute_oslogin_role_name
}

data "google_iam_role" "service_account_user_role" {
  name = var.service_account_user_role_name
}