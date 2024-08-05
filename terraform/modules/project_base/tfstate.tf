# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "tfstate" {
  name                     = "tfstate.${google_project.main.project_id}.eave.fyi" # This is hard-coded to eave.fyi because the project id is in the name so it's already unique.
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

  uniform_bucket_level_access = true
}