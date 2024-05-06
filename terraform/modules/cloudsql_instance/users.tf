# variable "users" {
#   type = map(object({
#     email     = string,
#     user_type = string,
#   }))

#   default = {}

#   description = "user_type: CLOUD_IAM_USER, CLOUD_IAM_GROUP, CLOUD_IAM_SERVICE_ACCOUNT. Built-in auth not supported."
# }

# resource "google_sql_user" "users" {
#   for_each = var.users

#   instance        = google_sql_database_instance.default.name
#   name            = trimsuffix(each.value.email, ".gserviceaccount.com")
#   type            = each.value.user_type
#   password        = null # only IAM supported
#   deletion_policy = "ABANDON"
# }