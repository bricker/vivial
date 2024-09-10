module "kubernetes_service" {
  for_each = [ local.app_name, local.internal_analytics_app_name ]

  source       = "../../modules/kube_service"
  namespace    = var.kube_namespace_name
  service_name = each.value
  service_port = local.service_port
  app_port     = local.app_port
}
