// https://registry.terraform.io/modules/GoogleCloudPlatform/sql-db/google/latest

locals {
  preset_development = contains(["STG", "DEV"], var.environment)
  preset_production = var.environment == "PROD"
}

variable "instance_name" {
  type = string
}

variable "environment" {
  type = string

  validation {
    condition = contains(["PROD", "STG", "DEV"], var.environment)
    error_message = "Valid values: PROD, STG, DEV"
  }
}

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "zone" {
  type = string
}

data "google_compute_network" "default_network" {
  name = "default"
  project = var.project_id
}

resource "google_sql_database_instance" "default" {
  name                 = var.instance_name
  database_version     = "POSTGRES_15"
  instance_type        = "CLOUD_SQL_INSTANCE"
  deletion_protection  = true
  # encryption_key_name  = null
  # maintenance_version  = "POSTGRES_15_5.R20240130.00_05"
  # master_instance_name = null
  project              = var.project_id
  region               = var.region
  # root_password        = null # sensitive

  settings {
    # activation_policy           = "ALWAYS"
    availability_type           = local.preset_production ? "REGIONAL" : "ZONAL"
    # collation                   = null
    connector_enforcement       = "REQUIRED"
    deletion_protection_enabled = true
    disk_autoresize             = local.preset_production
    disk_autoresize_limit       = 0
    disk_size                   = local.preset_production ? 100 : 10
    disk_type                   = "PD_SSD"
    edition                     = local.preset_production ? "ENTERPRISE_PLUS" : "ENTERPRISE"
    # pricing_plan                = "PER_USE"
    tier                        = local.preset_production ? "db-f1-micro" : "db-f1-micro"
    # time_zone                   = null
    user_labels                 = {}
    backup_configuration {
      binary_log_enabled             = local.preset_production
      enabled                        = local.preset_production
      # location                       = null
      point_in_time_recovery_enabled = local.preset_production
      start_time                     = "19:00"
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
      # query_plans_per_minute  = 5
      # query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
    ip_configuration {
      # allocated_ip_range                            = null
      enable_private_path_for_google_cloud_services = true
      ipv4_enabled                                  = true
      private_network                               = data.google_compute_network.default_network.id
      require_ssl                                   = false
      # ssl_mode                                      = null
    }
    location_preference {
      # follow_gae_application = null
      # secondary_zone         = null
      zone                   = var.zone
    }
    maintenance_window {
      day          = 7
      hour         = 0
      update_track = "stable"
    }
    password_validation_policy {
      complexity                  = "COMPLEXITY_DEFAULT"
      disallow_username_substring = true
      enable_password_policy      = true
      min_length                  = 20
      # password_change_interval    = null
      reuse_interval              = 10
    }
  }
}
