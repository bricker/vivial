# # # Create core Eave CloudSQL Instance
# # module "cloudsql_eave_core" {
# #   source        = "../../modules/cloud_sql"
# #   project_id    = local.project_id
# #   region        = local.region
# #   zone          = local.zone
# #   instance_name = "eave-pg-core"
# #   environment   = local.environment


# #   # {
# #   #   "bryan@eave.fyi" = {
# #   #     email = "bryan@eave.fyi",
# #   #     user_type = "CLOUD_IAM_USER"
# #   #   }
# #   # },
# #   # {
# #   #   "liam@eave.fyi" = {
# #   #     email = "liam@eave.fyi",
# #   #     user_type = "CLOUD_IAM_USER"
# #   #   }
# #   # },
# #   # {
# #   #   "eave-devs" = {
# #   #     email = local.developers_group_email,
# #   #     user_type = "CLOUD_IAM_GROUP" # Not supported for Postgres
# #   #   }
# #   # },
# # }

# resource "google_sql_database_instance" "eave_pg_core" {
#   name                = "eave-pg-core"
#   database_version    = "POSTGRES_15"
#   instance_type       = "CLOUD_SQL_INSTANCE"
#   deletion_protection = true
#   project = local.project_id
#   region  = local.region

#   settings {
#     availability_type = local.preset_production ? "REGIONAL" : "ZONAL"
#     connector_enforcement       = "REQUIRED"
#     deletion_protection_enabled = true
#     disk_autoresize             = local.preset_production
#     disk_autoresize_limit       = 0
#     disk_size                   = local.preset_production ? 100 : 10
#     disk_type                   = "PD_SSD"
#     edition                     = local.preset_production ? "ENTERPRISE_PLUS" : "ENTERPRISE"
#     tier = local.preset_production ? "db-f1-micro" : "db-f1-micro"
#     backup_configuration {
#       binary_log_enabled = local.preset_production
#       enabled            = local.preset_production
#       point_in_time_recovery_enabled = local.preset_production
#       start_time                     = "19:00"
#       transaction_log_retention_days = 7
#       backup_retention_settings {
#         retained_backups = 7
#         retention_unit   = "COUNT"
#       }
#     }
#     database_flags {
#       name  = "cloudsql.iam_authentication"
#       value = "on"
#     }
#     database_flags {
#       name  = "max_connections"
#       value = "100"
#     }
#     insights_config {
#       query_insights_enabled = true
#       record_application_tags = true
#       record_client_address   = true
#     }
#     ip_configuration {
#       enable_private_path_for_google_cloud_services = true
#       ipv4_enabled                                  = true
#       private_network                               = data.google_compute_network.default_network.id
#       require_ssl                                   = true
#       ssl_mode                                      = "TRUSTED_CLIENT_CERTIFICATE_REQUIRED" # ENCRYPTED_ONLY, TRUSTED_CLIENT_CERTIFICATE_REQUIRED, ALLOW_UNENCRYPTED_AND_ENCRYPTED
#     }
#     location_preference {
#       zone = local.zone
#     }
#     maintenance_window {
#       day          = 7
#       hour         = 0
#       update_track = "stable"
#     }
#     password_validation_policy {
#       complexity                  = "COMPLEXITY_DEFAULT"
#       disallow_username_substring = true
#       enable_password_policy      = true
#       min_length                  = 20
#       reuse_interval = 10
#     }
#   }
# }

# resource "google_sql_database" "databases" {
#   for_each = toset(concat(
#     [
#       "eave",
#       "playground-todoapp",
#     ],
#     [ for mbid, mb in local.metabase_instances: "metabase_db_${mbid}" ]
#   ))

#   name     = each.value
#   instance = google_sql_database_instance.eave_pg_core.name
# }

# resource "google_sql_user" "users" {
#   for_each = merge(
#     {
#       "core-api" = {
#         email     = module.apps_service_accounts["core-api"].gsa.email,
#         user_type = "CLOUD_IAM_SERVICE_ACCOUNT",
#       },
#       "playground-todoapp" = {
#         email     = module.apps_service_accounts["playground-todoapp"].gsa.email,
#         user_type = "CLOUD_IAM_SERVICE_ACCOUNT",
#       },
#     },
#     {
#       for mbid, mb in local.metabase_instances:
#         "metabase_app_${mbid}" => {
#           # email     = module.apps_service_accounts["core-api"].service_account.email,
#           user_type = "CLOUD_IAM_SERVICE_ACCOUNT",
#         }
#     }
#   )


#   instance        = google_sql_database_instance.eave_pg_core.name
#   name            = trimsuffix(each.value.email, ".gserviceaccount.com")
#   type            = each.value.user_type
#   password        = null # only IAM supported
#   deletion_policy = "ABANDON"
# }