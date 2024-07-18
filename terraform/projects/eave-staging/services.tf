locals {
  enabled_services = toset([
    "aiplatform.googleapis.com",          # Vertex AI API
    "artifactregistry.googleapis.com",    # Artifact Registry API
    "bigquery.googleapis.com",            # BigQuery API
    "certificatemanager.googleapis.com",  # Certificate Manager API
    "cloudaicompanion.googleapis.com",    # Gemini
    "cloudbuild.googleapis.com",          # Cloud Build API
    "cloudkms.googleapis.com",            # Cloud Key Management Service (KMS) API
    "compute.googleapis.com",             # Compute Engine API
    "container.googleapis.com",           # Kubernetes Engine API
    "containersecurity.googleapis.com",   # Container Security API
    "containerregistry.googleapis.com",   # Container Registry API
    "dataflow.googleapis.com",            # Dataflow API
    "dlp.googleapis.com",                 # Data Loss Prevention
    "dns.googleapis.com",                 # Cloud DNS API
    "domains.googleapis.com",             # Cloud Domains API
    "iam.googleapis.com",                 # Identity and Access Management (IAM) API
    "iap.googleapis.com",                 # Identity-Aware Proxy API
    "iamcredentials.googleapis.com",      # IAM Service Account Credentials API
    "logging.googleapis.com",             # Cloud Logging API
    "monitoring.googleapis.com",          # Cloud Monitoring API
    "networkconnectivity.googleapis.com", # Network Connectivity API
    "pubsub.googleapis.com",              # Cloud Pub/Sub API
    "secretmanager.googleapis.com",       # Secret Manager API
    "servicenetworking.googleapis.com",   # Service Networking API
    "sourcerepo.googleapis.com",          # Cloud Source Repositories API
    "sqladmin.googleapis.com",            # Cloud SQL Admin API
    "storage-api.googleapis.com",         # Google Cloud Storage JSON API
  ])
}

resource "google_project_service" "services" {
  for_each = local.enabled_services
  service  = each.value

  disable_dependent_services = false
  disable_on_destroy         = false
}