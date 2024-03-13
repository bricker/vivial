# // https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/runtimeconfig_config

# resource "google_runtimeconfig_config" "eave-app-configs" {
#   name        = "eave-app-configs"
#   description = "Non-sensitive application configurations"
# }

# resource "google_runtimeconfig_variable" "OPENAI_API_ORG" {
#   parent = google_runtimeconfig_config.eave-app-configs.name
#   name   = "configs/OPENAI_API_ORG"
#   text   = "..."
# }

# resource "google_runtimeconfig_variable" "EAVE_GITHUB_APP_CLIENT_ID" {
#   parent = google_runtimeconfig_config.eave-app-configs.name
#   name   = "configs/EAVE_GITHUB_APP_CLIENT_ID"
#   text   = "..."
# }

# resource "google_runtimeconfig_variable" "REDIS_TLS_CA" {
#   parent = google_runtimeconfig_config.eave-app-configs.name
#   name   = "configs/REDIS_TLS_CA"
#   text   = "..."
# }

# resource "google_runtimeconfig_variable" "REDIS_CONNECTION" {
#   parent = google_runtimeconfig_config.eave-app-configs.name
#   name   = "configs/REDIS_CONNECTION"
#   text   = "..."
# }