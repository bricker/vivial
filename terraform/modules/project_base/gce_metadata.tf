# `metadata_item` is used instead of authoritative `metadata` because GCP automatically creates and manages some metadata items (eg GKE).

moved {
  from = google_compute_project_metadata_item.enable_oslogin
  to   = google_compute_project_metadata_item.metadata_items["enable-oslogin"]
}

moved {
  from = google_compute_project_metadata_item.enable_oslogin_2fa
  to   = google_compute_project_metadata_item.metadata_items["enable-oslogin-2fa"]
}

resource "google_compute_project_metadata_item" "metadata_items" {
  for_each = {
    # Mandatory for SOC-2 compliance
    "enable-oslogin" = "TRUE",

    # Mandatory for SOC-2 compliance
    "enable-oslogin-2fa" = "TRUE",

    # Used by VM Manager
    # enable-osconfig is set to TRUE by default for _new_ projects when the `compute.requireOsConfig` policy is enabled, which is it for our org.
    # This key is here so that the item is added to existing projects that were created before the policy was enabled.
    # Mandatory for SOC-2 compliance
    "enable-osconfig" = "TRUE",

    # Used by VM Manager
    # Mandatory for SOC-2 compliance
    "enable-guest-attributes" = "TRUE",
  }

  key   = each.key
  value = each.value
}
