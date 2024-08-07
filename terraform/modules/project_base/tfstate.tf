resource "google_storage_bucket" "terraform" {
  name                     = "terraform.${google_project.main.project_id}.eave.fyi" # This is hard-coded to eave.fyi because the project id is in the name so it's already unique.
  force_destroy            = false
  location                 = "us-central1" # This is hardcoded because it's just for developers
  storage_class            = "STANDARD"
  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true
}