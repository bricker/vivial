# Create core Eave CloudSQL Instance
module "cloudsql_eave_core" {
  source        = "../../modules/cloud_sql"
  project_id    = local.project_id
  region        = local.region
  zone          = local.zone
  instance_name = "eave-pg-core"
  environment   = local.environment

  databases = [
    "eave",
    "metabase",
    "playground-todoapp",
  ]

  users = {
    "core-api" = {
      email     = module.apps_service_accounts["core-api"].service_account.email,
      user_type = "CLOUD_IAM_SERVICE_ACCOUNT",
    },
    "metabase" = {
      email     = module.apps_service_accounts["metabase"].service_account.email,
      user_type = "CLOUD_IAM_SERVICE_ACCOUNT",
    },
    "playground-todoapp" = {
      email     = module.apps_service_accounts["playground-todoapp"].service_account.email,
      user_type = "CLOUD_IAM_SERVICE_ACCOUNT",
    },
  }

  # {
  #   "bryan@eave.fyi" = {
  #     email = "bryan@eave.fyi",
  #     user_type = "CLOUD_IAM_USER"
  #   }
  # },
  # {
  #   "liam@eave.fyi" = {
  #     email = "liam@eave.fyi",
  #     user_type = "CLOUD_IAM_USER"
  #   }
  # },
  # {
  #   "eave-devs" = {
  #     email = local.developers_group_email,
  #     user_type = "CLOUD_IAM_GROUP" # Not supported for Postgres
  #   }
  # },
}