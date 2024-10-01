resource "kubernetes_secret" "app" {
  lifecycle {
    prevent_destroy = true
  }

  metadata {
    name      = local.app_name
    namespace = var.kube_namespace_name

    labels = {
      app = local.app_name
    }
  }

  type = "Opaque"
  data = {
  }
}