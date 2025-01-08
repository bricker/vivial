moved {
  from = module.kubernetes_service
  to   = module.kubernetes_services["default"]
}

moved {
  from = module.iap_app_kubernetes_service
  to   = module.kubernetes_services["iap"]
}

module "kubernetes_services" {
  for_each = {
    default = {
      name        = local.app_name
      iap_enabled = var.root_iap_enabled
    }
    iap = {
      name        = "${local.app_name}-iap"
      iap_enabled = true
    }
    healthchecks = {
      name        = "${local.app_name}-healthchecks"
      iap_enabled = false
    }
  }

  source                            = "../../modules/kube_service"
  namespace                         = var.kube_namespace_name
  service_name                      = each.value.name
  service_port                      = local.service_port
  app_name                          = local.app_name
  app_port                          = local.app_port
  iap_oauth_client_kube_secret_name = var.iap_oauth_client_kube_secret_name
  iap_oauth_client_id               = var.iap_oauth_client_id
  iap_enabled                       = each.value.iap_enabled
}

moved {
  from = module.service_backend_policy.kubernetes_manifest.backend_policy
  to   = module.kubernetes_service.kubernetes_manifest.backend_policy
}

moved {
  from = module.iap_service_backend_policy.kubernetes_manifest.backend_policy
  to   = module.kubernetes_services["iap"].kubernetes_manifest.backend_policy
}
