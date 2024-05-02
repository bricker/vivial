resource "kubernetes_manifest" "managed_certificate" {
  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "ManagedCertificate"
    metadata = {
      name = "${local.app_name}-cert"
      namespace = local.kube_namespace
    }

    spec = {
      domains = [
        "api.${var.root_domain}"
      ]
    }
  }
}
