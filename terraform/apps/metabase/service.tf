resource "kubernetes_service" "instances" {
  for_each = var.metabase_instances

  metadata {
    name = "mb-${each.value.metabase_instance_id}"
    namespace = var.kube_namespace_name
    labels = {
      app = "mb-${each.value.metabase_instance_id}"
    }
  }

  spec {
    selector = {
      app = "mb-${each.key}"
    }

    type = "NodePort"
    port {
      protocol = "TCP"
      name = local.service_port.name
      port = local.service_port.number
      target_port = local.app_port.name
    }
  }
}

# https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_health_check
resource "kubernetes_manifest" "instances_healthcheck_policy" {
  for_each = var.metabase_instances

  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "HealthCheckPolicy"
    metadata = {
      name = "mb-${each.value.metabase_instance_id}"
      namespace = var.kube_namespace_name

      labels = {
        app = "mb-${each.value.metabase_instance_id}"
      }
    }

    spec = {
      default = {
        checkIntervalSec = 30
        timeoutSec = 25
        healthyThreshold = 1
        unhealthyThreshold = 2
        logConfig = {
          enabled = true
        }
        config = {
          type = "HTTP"
          httpHealthCheck = {
            port = local.app_port.number
            requestPath = "/api/health"
            # response = jsonencode({"status":"ok"})
          }
        }
      }

      targetRef = {
        group = "" # This is a required attribute, can be empty
        kind = "Service"
        name = kubernetes_service.instances[each.key].metadata[0].name
      }
    }
  }
}
