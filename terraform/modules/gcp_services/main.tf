resource "google_project_service" "services" {
  for_each = toset([
    "admin.googleapis.com",                # Admin SDK API (Google Workspace), used by Thoropass
    "aiplatform.googleapis.com",           # Vertex AI API
    "artifactregistry.googleapis.com",     # Artifact Registry API
    "bigquery.googleapis.com",             # BigQuery API
    "bigtableadmin.googleapis.com",        # Bigtable Admin API, used by Thoropass
    "certificatemanager.googleapis.com",   # Certificate Manager API
    "cloudasset.googleapis.com",           # Cloud Asset API, required for compliance
    "cloudaicompanion.googleapis.com",     # Gemini
    "cloudbilling.googleapis.com",         # Cloud Billing
    "cloudbuild.googleapis.com",           # Cloud Build API
    "cloudkms.googleapis.com",             # Cloud Key Management Service (KMS) API
    "cloudresourcemanager.googleapis.com", # Cloud Resource Manager API, required by Terraform and Thoropass
    "compute.googleapis.com",              # Compute Engine API
    "container.googleapis.com",            # Kubernetes Engine API
    "containersecurity.googleapis.com",    # Container Security API
    "containerregistry.googleapis.com",    # Container Registry API
    "dataflow.googleapis.com",             # Dataflow API
    "datastream.googleapis.com",           # Datastream API
    "dlp.googleapis.com",                  # Data Loss Prevention
    "dns.googleapis.com",                  # Cloud DNS API
    "domains.googleapis.com",              # Cloud Domains API
    "firewallinsights.googleapis.com",     # Firewall Insights
    "iam.googleapis.com",                  # Identity and Access Management (IAM) API
    "iap.googleapis.com",                  # Identity-Aware Proxy API
    "iamcredentials.googleapis.com",       # IAM Service Account Credentials API
    "logging.googleapis.com",              # Cloud Logging API
    "memorystore.googleapis.com",          # Memorystore API
    "monitoring.googleapis.com",           # Cloud Monitoring API
    "networkconnectivity.googleapis.com",  # Network Connectivity API
    "networkmanagement.googleapis.com",    # Network Management API
    "osconfig.googleapis.com",             # VM Manager (OS Config API), required for compliance
    "places.googleapis.com",
    "places-backend.googleapis.com",
    "pubsub.googleapis.com",            # Cloud Pub/Sub API
    "pubsublite.googleapis.com",        # Pub/Sub Lite API, used by Thoropass
    "routes.googleapis.com",            # Maps Routing API
    "secretmanager.googleapis.com",     # Secret Manager API
    "servicenetworking.googleapis.com", # Service Networking API
    "serviceusage.googleapis.com",      # Service Usage API, used by Thoropass
    "sourcerepo.googleapis.com",        # Cloud Source Repositories API
    "sqladmin.googleapis.com",          # Cloud SQL Admin API
    "storage-api.googleapis.com",       # Google Cloud Storage JSON API
  ])

  project = var.project_id
  service = each.value

  disable_dependent_services = false
  disable_on_destroy         = false
}