variable "base_roles" {
  type=set(string)
  default = []
}

variable "role_id" {
  type=string
}

variable "title" {
  type=string
}

variable "description" {
  type=string
  nullable = true
  default=null
}

data "google_iam_role" "base_roles" {
  for_each = var.base_roles
  name = each.value
}

resource "google_project_iam_custom_role" "custom_role" {
  role_id     = var.role_id
  title       = var.title
  description = var.description
  # https://cloud.google.com/knowledge/kb/permission-error-for-custom-role-000004670
  permissions = setsubtract(distinct(flatten(
    [for _, role in data.google_iam_role.base_roles: role.included_permissions]
  )), ["resourcemanager.projects.list"])
}

output "role" {
  value = google_project_iam_custom_role.custom_role
}
