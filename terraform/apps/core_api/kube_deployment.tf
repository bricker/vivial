moved {
  from = kubernetes_deployment.app
  to   = kubernetes_deployment.app["core-api"]
}

resource "kubernetes_deployment" "app" {
  for_each = {
    (local.app_name) = {
      app_name            = local.app_name,
      deploy_name         = local.app_name,
      analytics_disabled  = false,
      ingest_api_base_url = "http://${local.internal_analytics_app_name}.${var.kube_namespace_name}.svc.cluster.local"
      match_labels = {
        app       = local.app_name
        app_group = local.app_name
      }
    },
    (local.internal_analytics_app_name) = {
      app_name            = local.internal_analytics_app_name,
      deploy_name         = local.internal_analytics_app_name,
      analytics_disabled  = true,
      ingest_api_base_url = "intentionally-not-a-url"
      match_labels = {
        app_group = local.app_name
        app       = local.internal_analytics_app_name
      }
    }
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations["kubectl.kubernetes.io/restartedAt"],
    ]
  }

  wait_for_rollout = false

  metadata {
    name      = each.value.deploy_name
    namespace = var.kube_namespace_name
    labels = {
      app = each.value.app_name
    }
  }

  spec {
    selector {
      match_labels = each.value.match_labels
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
        name   = each.value.app_name
        labels = each.value.match_labels
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
            name  = "EAVE_DB_NAME"
            value = google_sql_database.app.name
          }
          env {
            name  = "EAVE_DB_USER"
            value = google_sql_user.app.name
          }
          env {
            name  = "EAVE_DB_HOST"
            value = "127.0.0.1"
          }
          env {
            name  = "EAVE_DB_PORT"
            value = local.cloudsql_proxy_port.number
          }
          env {
            name  = "GUNICORN_CMD_ARGS"
            value = "--bind=0.0.0.0:${local.app_port.number} --workers=3 --timeout=90"
          }
          env {
            name  = "EAVE_ANALYTICS_DISABLED"
            value = each.value.analytics_disabled ? "1" : "0"
          }
          env {
            name  = "EAVE_INGEST_BASE_URL"
            value = each.value.ingest_api_base_url
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

        container {
          name  = "cloud-sql-proxy"
          image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:${local.cloudsql_proxy_version}"

          port {
            name           = local.clousql_proxy_healthcheck_port.name
            container_port = local.clousql_proxy_healthcheck_port.number
          }

          port {
            name           = local.cloudsql_proxy_port.name
            container_port = local.cloudsql_proxy_port.number
          }

          resources {
            # requests and limits must always be the same on Autopilot clusters without bursting.
            # if requests is omitted, the limits values are used.
            limits = {
              cpu    = "500m"
              memory = "2Gi"

              # Necessary to prevent perpetual diff
              # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
              "ephemeral-storage" = "1Gi"
            }
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

          args = [
            # Enable healthcheck endpoints for kube probes
            "--health-check",
            "--http-address=0.0.0.0",                                     # Bind to all interfaces so that the Kubernetes control plane can communicate with this process.
            "--http-port=${local.clousql_proxy_healthcheck_port.number}", # This is the default

            # If connecting from a VPC-native GKE cluster, you can use the
            # following flag to have the proxy connect over private IP
            "--private-ip",

            # If you are not connecting with Automatic IAM, you can delete
            # the following flag.
            "--auto-iam-authn",

            # tcp should be set to the port the proxy should listen on
            # and should match the DB_PORT value set above.
            # Defaults: MySQL: 3306, Postgres: 5432, SQLServer: 1433
            "--port=${local.cloudsql_proxy_port.number}",
            "--structured-logs",
            # - "--unix-socket /cloudsql"
            data.google_sql_database_instance.given.connection_name,
          ]

          startup_probe {
            period_seconds    = 1
            timeout_seconds   = 5
            failure_threshold = 20
            http_get {
              path = "/startup"
              port = local.clousql_proxy_healthcheck_port.name
            }
          }

          # The documentation does not recommend using the readiness probe.
          # The cloud-sql-proxy readiness probe checks for issues that can usually resolve themselves, so this check could restart the container unnecessarily.

          liveness_probe {
            initial_delay_seconds = 0
            period_seconds        = 60
            timeout_seconds       = 30
            failure_threshold     = 5
            http_get {
              path = "/liveness"
              port = local.clousql_proxy_healthcheck_port.name
            }
          }
        }
      }
    }
  }
}
