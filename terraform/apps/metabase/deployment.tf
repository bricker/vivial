resource "kubernetes_deployment" "instances" {
  for_each = var.metabase_instances

  wait_for_rollout = false

  metadata {
    name      = "mb-${each.value.metabase_instance_id}"
    namespace = var.kube_namespace_name
    labels = {
      app = "mb-${each.value.metabase_instance_id}"
    }
  }

  spec {
    selector {
      match_labels = {
        app = "mb-${each.value.metabase_instance_id}"
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
        name = "mb-${each.value.metabase_instance_id}"
        labels = {
          app = "mb-${each.value.metabase_instance_id}"
        }
      }
      spec {
        service_account_name = module.service_accounts[each.key].ksa_name

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
          name  = "metabase-enterprise"
          image = "metabase/metabase-enterprise:${local.metabase_enterprise_version}"

          port {
            name           = local.app_port.name
            container_port = local.app_port.number
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

          env_from {
            secret_ref {
              name = kubernetes_secret.shared.metadata[0].name
            }
          }
          env_from {
            secret_ref {
              name = kubernetes_secret.instances[each.key].metadata[0].name
            }
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.shared.metadata[0].name
            }
          }

          env {
            name  = "MB_DB_DBNAME"
            value = google_sql_database.instances[each.key].name
          }
          env {
            name  = "MB_DB_USER"
            value = google_sql_user.instances[each.key].name
          }
          env {
            name  = "MB_DB_TYPE"
            value = "postgres"
          }
          env {
            name  = "MB_DB_HOST"
            value = "127.0.0.1"
          }
          env {
            name  = "MB_DB_PORT"
            value = local.cloudsql_proxy_port.number
          }
          env {
            name  = "MB_JETTY_HOST"
            value = "0.0.0.0" # Default for Docker
          }
          env {
            name  = "MB_JETTY_PORT"
            value = local.app_port.number
          }


          # Necessary to prevent perpetual diff
          # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
          security_context {
            run_as_non_root            = false
            allow_privilege_escalation = false
            privileged                 = false
            read_only_root_filesystem  = false

            capabilities {
              add  = []
              drop = ["NET_RAW"]
            }
          }

          liveness_probe {
            period_seconds    = 60
            timeout_seconds   = 30
            failure_threshold = 5
            http_get {
              path = "/api/health"
              port = local.app_port.name
            }
          }

          startup_probe {
            # The metabase container takes a long time to boot up
            period_seconds    = 10
            failure_threshold = 30
            http_get {
              path = "/api/health"
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
            "${var.project.id}:${var.project.region}:${var.cloudsql_instance_name}",
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
