// https://registry.terraform.io/modules/GoogleCloudPlatform/sql-db/google/latest

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

resource "google_sql_database_instance" "eave_pg_core" {
  database_version     = "POSTGRES_14"
  deletion_protection  = true
  encryption_key_name  = null
  maintenance_version  = "POSTGRES_14_7.R20230530.01_04"
  master_instance_name = null
  name                 = "eave-pg-core"
  project              = var.project_id
  region               = var.region
  root_password        = null # sensitive
  settings {
    activation_policy           = "ALWAYS"
    availability_type           = "ZONAL"
    collation                   = null
    connector_enforcement       = "NOT_REQUIRED"
    deletion_protection_enabled = true
    disk_autoresize             = true
    disk_autoresize_limit       = 0
    disk_size                   = 10
    disk_type                   = "PD_SSD"
    pricing_plan                = "PER_USE"
    tier                        = "db-g1-small"
    time_zone                   = null
    user_labels                 = {}
    backup_configuration {
      binary_log_enabled             = false
      enabled                        = false
      location                       = null
      point_in_time_recovery_enabled = false
      start_time                     = "08:00"
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 7
        retention_unit   = "COUNT"
      }
    }
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
    ip_configuration {
      allocated_ip_range = null
      ipv4_enabled       = true
      private_network    = null
      require_ssl        = false
    }
    location_preference {
      follow_gae_application = null
      secondary_zone         = null
      zone                   = "us-central1-f"
    }
    maintenance_window {
      day          = 7
      hour         = 0
      update_track = null
    }
    password_validation_policy {
      complexity                  = "COMPLEXITY_DEFAULT"
      disallow_username_substring = true
      enable_password_policy      = true
      min_length                  = 16
      password_change_interval    = "172800s"
      reuse_interval              = 5
    }
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
