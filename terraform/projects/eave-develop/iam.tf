# module "custom_developer_role" {
#   source  = "../../modules/custom_role"
#   role_id = "eave.developers"
#   title   = "Eave Developers"
#   base_roles = [
#   ]
# }

# resource "google_project_iam_binding" "project_developer_role_members" {
#   project = data.google_project.default.id
#   role    = module.custom_developer_role.id
#   members = [
#     "group:developers@eave.fyi",
#   ]
# }

resource "google_project_iam_member" "project_developer_editors" {
  project = data.google_project.default.id
  role    = "roles/editor"
  member  = "group:developers@eave.fyi"
}

resource "google_project_iam_member" "project_developer_kms" {
  project = data.google_project.default.id
  role    = "roles/cloudkms.signerVerifier"
  member  = "group:developers@eave.fyi"
}

# resource "google_project_iam_member" "leilenah_kms" {
#   project = data.google_project.default.id
#   role    = "roles/cloudkms.admin"
#   member  = "user:leilenah@eave.fyi"
# }
