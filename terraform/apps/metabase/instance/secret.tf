resource "kubernetes_secret" "app" {
  metadata {
    name = local.app_name
    namespace = var.kube_namespace_name

    labels = {
      app = local.app_name
    }
  }

  type = "Opaque"
  data = {
    MB_ENCRYPTION_SECRET_KEY = var.MB_INSTANCE_SECRETS.MB_ENCRYPTION_SECRET_KEY
    MB_JWT_SHARED_SECRET = var.MB_INSTANCE_SECRETS.MB_JWT_SHARED_SECRET
  }
}