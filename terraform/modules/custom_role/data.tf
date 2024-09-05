data "google_iam_role" "base_roles" {
  for_each = var.base_roles
  name     = each.value
}
