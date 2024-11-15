resource "google_project" "managed" {
  lifecycle {
    prevent_destroy = true
  }

  for_each = local.managed_projects

  billing_account     = local.billing_account
  org_id              = local.org_id
  project_id          = each.value
  name                = each.value
  auto_create_network = false
}

module "gcp_services" {
  source   = "../../modules/gcp_services"
  for_each = local.managed_projects

  project_id = each.value
}

resource "google_storage_bucket" "terraform" {
  lifecycle {
    prevent_destroy = true
  }

  for_each = local.managed_projects

  project                     = each.value
  name                        = "terraform.${each.value}.eave.fyi" # This is hard-coded to eave.fyi because the project id is in the name so it's already unique.
  force_destroy               = false
  location                    = "us-central1" # This is hardcoded because it's just for developers
  storage_class               = "STANDARD"
  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  logging {
    log_bucket = "logs.${each.value}.eave.fyi"
  }
}
