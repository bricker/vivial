// https://registry.terraform.io/modules/GoogleCloudPlatform/sql-db/google/latest

variable "instance_name" {
  type = string
}

variable "instance_tier" {
  type = string
}

variable "instance_disk_type" {
  type = string
}

variable "instance_disk_size" {
  type = number
}

variable "instance_backup_enabled" {
  type = bool
}

variable "instance_zone" {
  type = string
}

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
  maintenance_version  = "POSTGRES_14_9.R20230830.01_01"
  master_instance_name = null
  name                 = var.instance_name
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
    disk_size                   = 100
    disk_type                   = var.instance_disk_type
    pricing_plan                = "PER_USE"
    tier                        = var.instance_tier
    time_zone                   = null
    user_labels                 = {}
    backup_configuration {
      binary_log_enabled             = false
      enabled                        = var.instance_backup_enabled
      location                       = "us"
      point_in_time_recovery_enabled = var.instance_backup_enabled
      start_time                     = "05:00"
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
      zone                   = var.instance_zone
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
      password_change_interval    = null
      reuse_interval              = 0
    }
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
