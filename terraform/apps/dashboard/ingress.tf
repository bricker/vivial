resource "kubernetes_manifest" "managed_certificate" {
  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "ManagedCertificate"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      domains = [module.dns.domain]
    }
  }
}

resource "kubernetes_manifest" "frontend_config" {
  # Standard app frontend config.
  manifest = {
    apiVersion = "networking.gke.io/v1beta1"
    kind       = "FrontendConfig"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      redirectToHttps = {
        enabled = true
        responseCodeName = "MOVED_PERMANENTLY_DEFAULT"
      }
    }
  }
}

resource "kubernetes_ingress_v1" "app" {
  metadata {
    name = local.app_name
    namespace = var.kube_namespace_name
    annotations = {
      "networking.gke.io/v1beta1.FrontendConfig" = kubernetes_manifest.frontend_config.manifest.metadata.name
      "networking.gke.io/managed-certificates" = kubernetes_manifest.managed_certificate.manifest.metadata.name
      "kubernetes.io/ingress.global-static-ip-name" = module.dns.address.name
      "kubernetes.io/ingress.class" = "gce"
    }

    labels = {
      app = local.app_name
    }
  }

  spec {
    ingress_class_name = "gce"

    default_backend {
      service {
        name = kubernetes_service.app.metadata[0].name
        port {
          name = local.service_port.name
        }
      }
    }
  }
}