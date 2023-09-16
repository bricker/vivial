resource "google_app_engine_application" "app" {
  auth_domain    = "gmail.com"
  database_type  = "CLOUD_DATASTORE_COMPATIBILITY"
  location_id    = "us-central"
  project        = "eavefyi-dev"
  serving_status = "SERVING"
  feature_settings {
    split_health_checks = true
  }
}

resource "google_app_engine_service_network_settings" "www" {
  project = "eavefyi-dev"
  service = "www"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

resource "google_app_engine_service_network_settings" "slack" {
  project = "eavefyi-dev"
  service = "slack"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

# __generated__ by Terraform from "api"
resource "google_app_engine_service_network_settings" "api" {
  project = "eavefyi-dev"
  service = "api"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

# __generated__ by Terraform
resource "google_app_engine_service_network_settings" "github" {
  project = "eavefyi-dev"
  service = "github"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

# __generated__ by Terraform from "confluence"
resource "google_app_engine_service_network_settings" "confluence" {
  project = "eavefyi-dev"
  service = "confluence"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}

# __generated__ by Terraform from "jira"
resource "google_app_engine_service_network_settings" "jira" {
  project = "eavefyi-dev"
  service = "jira"
  network_settings {
    ingress_traffic_allowed = "INGRESS_TRAFFIC_ALLOWED_INTERNAL_AND_LB"
  }
}
