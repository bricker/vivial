// https://registry.terraform.io/modules/GoogleCloudPlatform/sql-db/google/latest

resource "google_sql_database_instance" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name                = var.instance_name
  database_version    = "POSTGRES_15"
  instance_type       = "CLOUD_SQL_INSTANCE"
  deletion_protection = true

  settings {
    availability_type           = local.preset_production ? "REGIONAL" : "ZONAL"
    connector_enforcement       = "REQUIRED"
    deletion_protection_enabled = true
    disk_autoresize             = local.preset_production
    disk_autoresize_limit       = 0
    disk_size                   = local.preset_production ? 100 : 10
    disk_type                   = "PD_SSD"
    edition                     = local.preset_production ? "ENTERPRISE_PLUS" : "ENTERPRISE"
    tier                        = local.preset_production ? "db-perf-optimized-N-2" : "db-f1-micro"
    backup_configuration {
      binary_log_enabled             = false # Only supported for MySQL
      enabled                        = var.enable_backups
      point_in_time_recovery_enabled = var.enable_backups
      start_time                     = "19:00"
      transaction_log_retention_days = 6
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
      # Mandatory for compliance
      name  = "log_lock_waits"
      value = "on"
    }
    database_flags {
      # Mandatory for SOC-2 compliance
      name  = "log_statement"
      value = "ddl"
    }
    database_flags {
      # This helps clean up idle connections left by app instances that weren't gracefully terminated.
      name  = "idle_in_transaction_session_timeout"
      value = "30000"
    }
    database_flags {
      name  = "timezone"
      value = "UTC"
    }
    insights_config {
      query_insights_enabled  = true
      record_application_tags = true
      record_client_address   = true
    }
    ip_configuration {
      enable_private_path_for_google_cloud_services = true
      ipv4_enabled                                  = false # Mandatory for SOC-2 compliance
      private_network                               = var.google_compute_network.id
      ssl_mode                                      = "TRUSTED_CLIENT_CERTIFICATE_REQUIRED" # ENCRYPTED_ONLY, TRUSTED_CLIENT_CERTIFICATE_REQUIRED, ALLOW_UNENCRYPTED_AND_ENCRYPTED
      # allocated_ip_range = data.google_compute_global_address.given.name
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
