moved {
  from = module.kubernetes_service[local.app_name]
  to = module.kubernetes_service
}

module "kubernetes_service" {
  source       = "../../modules/kube_service"
  namespace    = var.kube_namespace_name
  service_name = each.value
  service_port = local.service_port
  app_port     = local.app_port
}
