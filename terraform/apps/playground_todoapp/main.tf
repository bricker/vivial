module "service_accounts" {
  source         = "../../modules/gke_app_service_account"
  project     = var.project
  kube_service_name            = kubernetes_service.app.metadata[0].name
  kube_namespace_name = var.kube_namespace_name
}

# Create custom role
module "app_iam_role" {
  source      = "../../modules/custom_role"
  project = var.project
  role_id     = "eave.playgroundTodoApp"
  title       = "Eave Playground Todo App"
  description = "Permissions needed by the Playground Todo App"
  base_roles  = [
    "roles/logging.logWriter",
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]

  members = [
    "serviceAccount:${module.service_accounts.gsa.email}"
  ]
}

resource "google_sql_database" "app" {
  name     = "playground-todoapp"
  instance = var.cloudsql_instance_name
}

resource "google_sql_user" "app" {
  instance        = var.cloudsql_instance_name
  name            = trimsuffix(module.service_accounts.gsa.email, ".gserviceaccount.com")
  type            = "CLOUD_IAM_SERVICE_ACCOUNT"
  password        = null # only IAM supported
  deletion_policy = "ABANDON"
}

resource "google_compute_global_address" "default" {
  name         = "playground-todoapp"
  address_type = "EXTERNAL"
}

resource "google_dns_record_set" "default" {
  managed_zone = var.dns_zone.name
  name = "${local.domain_prefix}.${var.dns_zone.dns_name}"
  type = "A"
  ttl  = 300
  rrdatas = [google_compute_global_address.default.address]
}

locals {
  domain = trimsuffix(google_dns_record_set.default.name, ".")
}