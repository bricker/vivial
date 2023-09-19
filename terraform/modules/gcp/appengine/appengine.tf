variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

resource "google_app_engine_application" "app" {
  auth_domain    = "gmail.com"
  database_type  = "CLOUD_DATASTORE_COMPATIBILITY"
  location_id    = var.region
  project        = var.project_id
  serving_status = "SERVING"
  feature_settings {
    split_health_checks = true
  }
}

resource "google_app_engine_service_network_settings" "www" {
  project = var.project_id
  service = "www"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

resource "google_app_engine_service_network_settings" "slack" {
  project = var.project_id
  service = "slack"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

# __generated__ by Terraform from "api"
resource "google_app_engine_service_network_settings" "api" {
  project = var.project_id
  service = "api"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

# __generated__ by Terraform
resource "google_app_engine_service_network_settings" "github" {
  project = var.project_id
  service = "github"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

# __generated__ by Terraform from "confluence"
resource "google_app_engine_service_network_settings" "confluence" {
  project = var.project_id
  service = "confluence"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

# __generated__ by Terraform from "jira"
resource "google_app_engine_service_network_settings" "jira" {
  project = var.project_id
  service = "jira"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}
