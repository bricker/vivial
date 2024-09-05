data "google_iam_role" "secret_accessor_role" {
  name = var.secret_accessor_role_name
}