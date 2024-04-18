variable "project_id" {
  type = string
}

variable "org_id" {
  type = string
}

variable "billing_account" {
  type = string
}

resource "google_project" "main" {
  # folder_id           = null
  billing_account     = var.billing_account
  org_id              = var.org_id
  project_id          = var.project_id
  name                = var.project_id
  auto_create_network = true
  skip_delete         = true
}