# module "gcp_secret_manager" {
#   source = "../../modules/secret_manager"

#   for_each = {
#     "EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64" = var.EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64
#     "SLACK_SYSTEM_BOT_TOKEN"                        = var.SLACK_SYSTEM_BOT_TOKEN
#     "OPENAI_API_KEY"                                = var.OPENAI_API_KEY
#   }

#   secret_id   = each.key
#   secret_data = each.value
# }