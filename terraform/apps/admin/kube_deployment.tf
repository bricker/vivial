resource "kubernetes_deployment" "app" {
  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations["kubectl.kubernetes.io/restartedAt"],
    ]
  }

  wait_for_rollout = false

  metadata {
    name      = local.app_name
    namespace = var.kube_namespace_name
    labels = {
      app = local.app_name
    }
  }

  spec {
    selector {
      match_labels = {
        app = local.app_name
      }
    }

    replicas = 2
    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_surge = "1"
      }
    }

    template {
      metadata {
        name = local.app_name
        labels = {
          app = local.app_name
        }
      }
      spec {
        service_account_name = module.service_accounts.ksa_name

        # Necessary to prevent perpetual diff
        # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
        toleration {
          effect   = "NoSchedule"
          key      = "kubernetes.io/arch"
          operator = "Equal"
          value    = "amd64"
        }

        # Necessary to prevent perpetual diff
        # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
        security_context {
          run_as_non_root = true

          seccomp_profile {
            type = "RuntimeDefault"
          }
        }

        container {
          name  = local.app_name
          image = "${data.google_artifact_registry_repository.docker.location}-docker.pkg.dev/${data.google_artifact_registry_repository.docker.project}/${data.google_artifact_registry_repository.docker.repository_id}/${local.app_name}:${var.release_version}"

          port {
            name           = local.app_port.name
            container_port = local.app_port.number
          }

          resources {
            # requests and limits must always be the same on Autopilot clusters without bursting.
            # if requests is omitted, the limits values are used.
            limits = {
              cpu    = "250m"
              memory = "1Gi"
              # Necessary to prevent perpetual diff
              # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
              "ephemeral-storage" = "1Gi"
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.app.metadata[0].name
            }
          }
          env_from {
            config_map_ref {
              name = var.shared_config_map_name
            }
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.app.metadata[0].name
            }
          }

          env {
            name  = "GUNICORN_CMD_ARGS"
            value = "--bind=0.0.0.0:${local.app_port.number} --workers=3 --timeout=90"
          }

          # Necessary to prevent perpetual diff
          # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
          security_context {
            run_as_non_root            = true
            allow_privilege_escalation = false
            privileged                 = false
            read_only_root_filesystem  = false

            capabilities {
              add  = []
              drop = ["NET_RAW"]
            }
          }

          readiness_probe {
            failure_threshold     = 2
            timeout_seconds       = 30
            period_seconds        = 30
            initial_delay_seconds = 15
            http_get {
              path = "/healthz"
              port = local.app_port.name
            }
          }

          liveness_probe {
            failure_threshold     = 5
            timeout_seconds       = 30
            period_seconds        = 30
            initial_delay_seconds = 15
            http_get {
              path = "/healthz"
              port = local.app_port.name
            }
          }
        }
      }
    }
  }
}
