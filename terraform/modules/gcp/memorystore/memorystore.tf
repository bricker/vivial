variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

# resource "google_redis_instance" "eave_redis" {
#   alternative_location_id = null
#   auth_enabled            = true
#   authorized_network      = "projects/${var.project_id}/global/networks/default"
#   connect_mode            = "DIRECT_PEERING"
#   customer_managed_key    = null
#   display_name            = null
#   labels                  = {}
#   location_id             = null
#   memory_size_gb          = 1
#   name                    = "eave-redis"
#   project                 = var.project_id
#   read_replicas_mode      = "READ_REPLICAS_DISABLED"
#   redis_configs           = {}
#   redis_version           = "REDIS_7_0"
#   region                  = var.region
#   replica_count           = 0
#   reserved_ip_range       = "10.217.33.0/29"
#   secondary_ip_range      = null
#   tier                    = "BASIC"
#   transit_encryption_mode = "SERVER_AUTHENTICATION"
#   persistence_config {
#     persistence_mode        = "DISABLED"
#     rdb_snapshot_period     = null
#     rdb_snapshot_start_time = null
#   }
#   timeouts {
#     create = null
#     delete = null
#     update = null
#   }
# }
