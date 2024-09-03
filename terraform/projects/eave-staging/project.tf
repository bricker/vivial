module "project_base" {
  source          = "../../modules/project_base"
  project_id      = local.project_id
  org_id          = local.org_id
  billing_account = local.billing_account
  subnet_region   = local.default_region
  root_domain     = local.root_domain
}
