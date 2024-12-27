module "kubernetes_service" {
  source       = "../../modules/kube_service"
  namespace    = var.kube_namespace_name
  service_name = local.app_name
  service_port = local.service_port
  app_port     = local.app_port
}
