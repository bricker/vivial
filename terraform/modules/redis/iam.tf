module "redis_user_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.redisUser"
  title       = "Redis User"
  description = "Access to connect to Redis"
  base_roles = [
    "roles/redis.dbConnectionUser",
  ]
}

resource "google_project_iam_binding" "project_redis_user_role_members" {
  lifecycle {
    prevent_destroy = true
  }

  project = data.google_project.default.project_id
  role    = module.redis_user_role.id
  members = var.redis_user_role_members
}
