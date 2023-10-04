variable "project_id" {
  type = string
}

variable "billing_account" {
  type = string
}

variable "org_id" {
  type = string
}

resource "google_project" "gcp_project" {
  auto_create_network = true
  billing_account     = var.billing_account
  folder_id           = null
  labels              = {}
  name                = var.project_id
  org_id              = var.org_id
  project_id          = var.project_id
  skip_delete         = null
  timeouts {
    create = null
    delete = null
    read   = null
    update = null
  }
}