# resource "google_project_iam_binding" "bigquery_data_owner" {
#   project = local.project_id
#   role    = "roles/bigquery.dataOwner"

#   members = [
#     "domain:eave.fyi"
#   ]
# }