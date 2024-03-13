// https://registry.terraform.io/modules/terraform-google-modules/bigquery/google/latest

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

locals {
  tables = {
    dbchanges = {
      table_id = "dbchanges",
      description = "DB Changes Atoms",
      schema = jsonencode([
        {
            name="table_name"
            description="The name of the table that was modified"
            type="STRING"
            mode="REQUIRED"
        },

        {
            name="operation"
            description="The table operation (INSERT, UPDATE, or DELETE)"
            type="STRING"
            mode="REQUIRED"
        },

        {
            name="timestamp"
            description="The timestamp of the table operation"
            type="TIMESTAMP"
            mode="REQUIRED"
        },

        {
            name="old_data"
            description="The row data before the change (will be NULL for INSERTs)"
            type="JSON"
            mode="NULLABLE"
        },

        {
            name="new_data"
            description="The row data after the change (will be NULL for DELETEs)"
            type="JSON"
            mode="NULLABLE"
        },
      ])
    },
  }
}

resource "google_bigquery_dataset" "eave_atoms_dataset" {
  # Dataset access is applied per-project using resource "google_bigquery_dataset_access"
  dataset_id                  = "internal_eave_atoms"
  friendly_name               = "Internal - Eave Atoms"
  description                 = "Internal storage for Eave Atoms"
  project = var.project_id
  location                    = var.region
  default_table_expiration_ms = null
}


resource "google_bigquery_table" "dbchanges_atoms" {
  depends_on = [ google_bigquery_dataset.eave_atoms_dataset ]
  for_each = local.tables

  dataset_id = google_bigquery_dataset.eave_atoms_dataset.dataset_id
  project   = var.project_id
  deletion_protection = true

  table_id   = each.value.table_id
  description = each.value.description
  schema = each.value.schema

  time_partitioning {
    type = "DAY"
  }
}