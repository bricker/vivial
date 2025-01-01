resource "google_redis_instance" "eave_redis" {
  name                    = "eave-redis"
  alternative_location_id = null
  auth_enabled            = true
  authorized_network      = "projects/${var.project_id}/global/networks/default"
  connect_mode            = "DIRECT_PEERING"
  memory_size_gb          = 8
  project                 = data.google_project.default.id
  # read_replicas_mode      = "READ_REPLICAS_DISABLED"
  redis_configs           = {}
  redis_version           = "REDIS_7_0"
  region                  = var.region
  replica_count           = 0
  reserved_ip_range       = "10.217.33.0/29"
  secondary_ip_range      = null
  tier                    = "BASIC"
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  persistence_config {
    persistence_mode        = "DISABLED"
    rdb_snapshot_period     = null
    rdb_snapshot_start_time = null
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
