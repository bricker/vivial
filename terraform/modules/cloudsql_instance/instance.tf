// https://registry.terraform.io/modules/GoogleCloudPlatform/sql-db/google/latest

variable "project" {
  type = object({
    region            = string
    zone              = string
    preset_production = bool
  })
}

variable "instance_name" {
  type = string
}

variable "network" {
  type = object({
    id = string
  })
}

resource "google_sql_database_instance" "default" {
  name                = var.instance_name
  database_version    = "POSTGRES_15"
  instance_type       = "CLOUD_SQL_INSTANCE"
  deletion_protection = true
  region              = var.project.region

  settings {
    availability_type           = var.project.preset_production ? "REGIONAL" : "ZONAL"
    connector_enforcement       = "REQUIRED"
    deletion_protection_enabled = true
    disk_autoresize             = var.project.preset_production
    disk_autoresize_limit       = 0
    disk_size                   = var.project.preset_production ? 100 : 10
    disk_type                   = "PD_SSD"
    edition                     = var.project.preset_production ? "ENTERPRISE_PLUS" : "ENTERPRISE"
    tier                        = var.project.preset_production ? "db-f1-micro" : "db-f1-micro"
    backup_configuration {
      binary_log_enabled             = var.project.preset_production
      enabled                        = var.project.preset_production
      point_in_time_recovery_enabled = var.project.preset_production
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
    database_flags {
      name  = "max_connections"
      value = "100"
    }
    database_flags {
      # Mandatory for SOC-2 compliance
      name  = "log_connections"
      value = "on"
    }
    database_flags {
      # Mandatory for SOC-2 compliance
      name  = "log_disconnections"
      value = "on"
    }
    database_flags {
      # Mandatory for SOC-2 compliance
      name  = "log_statement"
      value = "ddl"
    }
    insights_config {
      query_insights_enabled  = true
      record_application_tags = true
      record_client_address   = true
    }
    ip_configuration {
      enable_private_path_for_google_cloud_services = true
      ipv4_enabled                                  = true
      private_network                               = var.network.id
      require_ssl                                   = true
      ssl_mode                                      = "TRUSTED_CLIENT_CERTIFICATE_REQUIRED" # ENCRYPTED_ONLY, TRUSTED_CLIENT_CERTIFICATE_REQUIRED, ALLOW_UNENCRYPTED_AND_ENCRYPTED
    }
    location_preference {
      zone = var.project.zone
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
      reuse_interval              = 10
    }
  }
}

output "instance" {
  value = google_sql_database_instance.default
}