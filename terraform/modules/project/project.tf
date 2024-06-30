variable "project" {
  type = object({
    id = string
  })
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
  project_id          = var.project.id
  name                = var.project.id
  auto_create_network = false
  skip_delete         = true
}