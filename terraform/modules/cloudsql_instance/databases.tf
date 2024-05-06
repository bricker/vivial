# variable "databases" {
#   type    = set(string)
#   default = []
# }

# # FIXME: Set owner?
# resource "google_sql_database" "database" {
#   for_each = var.databases
#   name     = each.value
#   instance = google_sql_database_instance.default.name
# }