resource "google_project" "eavefyi-dev" {
  auto_create_network = true
  billing_account     = "013F5E-137CB0-B6AA2A"
  folder_id           = null
  labels              = {}
  name                = "eavefyi-dev"
  org_id              = "482990375115"
  project_id          = "eavefyi-dev"
  skip_delete         = null
  timeouts {
    create = null
    delete = null
    read   = null
    update = null
  }
}
