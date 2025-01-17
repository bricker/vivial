resource "google_redis_instance" "default" {
  lifecycle {
    prevent_destroy = true
  }

  name                    = "eave-redis"
  tier                    = "BASIC"
  authorized_network      = var.google_compute_network.id
  connect_mode            = "DIRECT_PEERING"
  memory_size_gb          = 2
  auth_enabled            = true
  transit_encryption_mode = "SERVER_AUTHENTICATION"
  redis_version           = "REDIS_7_0"
  redis_configs = {
    "maxmemory"        = "2000mb" # 2gb, minus 48mb for LRU buffering
    "maxmemory-policy" = "allkeys-lru"
  }

  persistence_config {
    persistence_mode = "DISABLED"
  }
}
