locals {
  app_name = "core-api"
  app_version = "latest"
  kube_namespace = "eave"
}


resource "kubernetes_deployment" "default" {
  metadata {
    name = "${local.app_name}-deployment"
    namespace = local.kube_namespace
    labels = {
      app = local.app_name
    }
  }

  spec {
    selector {
      match_labels = {
        app = "${local.app_name}-app"
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
        labels = {
          app = "${local.app_name}-app"
        }
      }
      spec {
        service_account_name = "ksa-app-${local.app_name}"

        container {
          name = local.app_name
          image = "${var.docker_repository.repository_id}/${local.app_name}:${local.app_version}"

          port {
            name = "app"
            container_port = 8000
          }

          resources {
            # requests and limits must always be the same on Autopilot clusters without bursting.
            # if requests is omitted, the limits values are used.
            limits = {
              cpu    = "250m"
              memory = "1Gi"
            }
          }

          env_from {
            secret_ref {
              name = "metabase-jwt-shared-secret"
            }
          }
          env_from {
            secret_ref {
              name = "core-api-secret"
            }
          }
          env_from {
            config_map_ref {
              name = "shared-configmap"
            }
          }
          env_from {
            config_map_ref {
              name = "core-api-configmap"
            }
          }

          env {
            name = "EAVE_DB_USER"
            value = "gsa-app-${local.app_name}@${var.project_id}.iam"
          }
          env {
            name = "EAVE_DB_HOST"
            value = "127.0.0.1"
          }
          env {
            name = "EAVE_DB_PORT"
            value = "5432"
          }
          env {
            name = "GUNICORN_CMD_ARGS"
            value = "--bind=0.0.0.0:8000 --workers=3 --timeout=90"
          }

          readiness_probe {
            http_get {
              path = "/status"
              port = "app"
            }
          }

          liveness_probe {
            failure_threshold = 5
            http_get {
              path = "/status"
              port = "app"
            }
          }
        }

        container {
          name = "cloud-sql-proxy"
          image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:latest"

          port {
            name = "healthcheck"
            container_port = 9090
          }

          port {
            name = "proxy"
            container_port = 5432
          }

          resources {
            # requests and limits must always be the same on Autopilot clusters without bursting.
            # if requests is omitted, the limits values are used.
            limits = {
              cpu    = "500m"
              memory = "2Gi"
            }
          }

          security_context {
            run_as_non_root = true
          }

          args = [
            # Enable healthcheck endpoints for kube probes
            "--health-check",
            "--http-address=0.0.0.0", # Bind to all interfaces so that the Kubernetes control plane can communicate with this process.
            "--http-port=9090", # This is the default

            # If connecting from a VPC-native GKE cluster, you can use the
            # following flag to have the proxy connect over private IP
            "--private-ip",

            # If you are not connecting with Automatic IAM, you can delete
            # the following flag.
            "--auto-iam-authn",

            # tcp should be set to the port the proxy should listen on
            # and should match the DB_PORT value set above.
            # Defaults: MySQL: 3306, Postgres: 5432, SQLServer: 1433
            "--port=5432",
            "--structured-logs",
            # - "--unix-socket /cloudsql"
            "${var.project_id}:${var.region}:eave-pg-core",
          ]

          startup_probe {
            period_seconds = 1
            timeout_seconds = 5
            failure_threshold = 20
            http_get {
              path = "/startup"
              port = "healthcheck"
            }
          }

          # The documentation does not recommend using the readiness probe.
          # The cloud-sql-proxy readiness probe checks for issues that can usually resolve themselves, so this check could restart the container unnecessarily.

          liveness_probe {
            initial_delay_seconds = 0
            period_seconds = 60
            timeout_seconds = 30
            failure_threshold = 5
            http_get {
              path = "/liveness"
              port = "healthcheck"
            }
          }
        }
      }
    }
  }
}
