variable "project_id" {
  type = string
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "tfstate" {
  name                     = "tfstate.${var.project_id}.eave.fyi"
  project                  = var.project_id
  force_destroy            = false
  location                 = "US"
  storage_class            = "STANDARD"
  public_access_prevention = "enforced"

  # logging {
  #   log_bucket = "logs.${var.project_id}.eave.fyi"
  # }
  versioning {
    enabled = true
  }
}
