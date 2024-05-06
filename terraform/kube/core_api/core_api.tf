locals {
  app_name = "core-api"
}

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "namespace" {
  type=string
}

variable "cloudsql_instance_id" {
  type=string
}

variable "db_name" {
  type=string
}

variable "domain" {
  type=string
}

variable "shared_frontend_config_name" {
  type=string
}

variable "shared_backend_config_name" {
  type=string
}

variable "static_ip_name" {
  type=string
}

variable "release_version" {
  type=string
}

variable "release_date" {
  type=string
}

variable "LOG_LEVEL" {
  type=string
  default = "debug"
}

resource "kubernetes_config_map" "core_api" {
  metadata {
    name = "${local.app_name}-configmap"
    namespace = var.namespace
  }

  data = {
    EAVE_DB_NAME = var.db_name
    GAE_SERVICE = local.app_name
    GAE_VERSION = var.release_version
    GAE_RELEASE_DATE = var.release_date
    LOG_LEVEL = var.LOG_LEVEL
  }
}

resource "kubernetes_secret" "core_api" {
  metadata {
    name = "${local.app_name}-secret"
    namespace = var.namespace
  }

  type = "Opaque"
  data = {
    METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64 = "${var.METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64}"
  }
}

resource "kubernetes_manifest" "core_api_managed_certificate" {
  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "ManagedCertificate"
    metadata = {
      name = "${local.app_name}-cert"
      namespace = var.namespace
    }

    spec = {
      domains = [var.domain]
    }
  }
}

resource "kubernetes_service_account" "core_api" {
  metadata {
    name = "ksa-app-${local.app_name}"
    namespace = var.namespace
    annotations = {
      "iam.gke.io/gcp-service-account" = "gsa-app-${local.app_name}@${var.project_id}.iam.gserviceaccount.com"
    }
  }
}

resource "kubernetes_service" "core_api" {
  metadata {
    name = "${local.app_name}"
    namespace = kubernetes_namespace.eave.metadata.0.name
    annotations = {
      "beta.cloud.google.com/backend-config" = jsonencode({"default": var.shared_backend_config_name})
    }
  }

  spec {
    selector = {
      "app" = "${local.app_name}-app"
    }

    type = "NodePort"
    port {
      name = "http"
      protocol = "TCP"
      port = 80
      target_port = "app"
    }
  }
}

resource "kubernetes_ingress_v1" "core_api" {
  metadata {
    name = "${local.app_name}-ingress"
    namespace = var.namespace
    annotations = {
      "networking.gke.io/v1beta1.FrontendConfig" = var.shared_frontend_config_name
      "networking.gke.io/managed-certificates" = kubernetes_manifest.core_api_managed_certificate.manifest.metadata.name
      "kubernetes.io/ingress.global-static-ip-name" = var.static_ip_name
      "kubernetes.io/ingress.class" = "gce"
    }

    labels = {
      "app" = "${local.app_name}-app"
    }
  }

  spec {
    # This does not work. Without the "ingress.class" annotation, the LB isn't created.
    ingress_class_name = "gce"

    # The NOOP service is meant to always fail. It prevents external traffic from accessing paths that aren't whitelisted here.
    # GKE provides a "default-http-backend" service that is used if defaultBackend isn't specified here.
    # However, the response that it returns is a 404 with a message that exposes details about the infrastructure, and is therefore unsuitable.
    # default_backend {
    #   service {
    #     name = "noop"
    #     port {
    #       number = 65535
    #     }
    #   }
    # }


    rule {
      host = var.domain
      http {
        # Supported public endpoint prefixes.
        # Everything else is only accessible from the cluster.
        # TODO: a better place to define these?

        path {
          path = "/status"
          backend {
            service {
              name = kubernetes_service.core_api.metadata.0.name
              port {
                name = "http"
              }
            }
          }
        }
        path {
          path = "/public"
          backend {
            service {
              name = kubernetes_service.core_api.metadata.0.name
              port {
                name = "http"
              }
            }
          }
        }
        path {
          path = "/oauth"
          backend {
            service {
              name = kubernetes_service.core_api.metadata.0.name
              port {
                name = "http"
              }
            }
          }
        }
        path {
          path = "/favicon.ico"
          backend {
            service {
              name = kubernetes_service.core_api.metadata.0.name
              port {
                name = "http"
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment" "core_api" {
  wait_for_rollout = false

  metadata {
    name = "${local.app_name}-deployment"
    namespace = var.namespace
    labels = {
      app = "${local.app_name}-app"
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
        service_account_name = kubernetes_service_account.core_api.metadata.0.name

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
          name = "${local.app_name}"
          image = "${var.docker_repository.location}-docker.pkg.dev/${var.docker_repository.project}/${var.docker_repository.repository_id}/${local.app_name}:${var.release.version}"

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
              # Necessary to prevent perpetual diff
              # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
              "ephemeral-storage" = "1Gi"
            }
          }

          # env_from {
          #   secret_ref {
          #     name = "metabase-jwt-shared-secret"
          #   }
          # }
          env_from {
            secret_ref {
              name = kubernetes_secret.core_api.metadata.0.name
            }
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.shared.metadata.0.name
            }
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.core_api.metadata.0.name
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

          # Necessary to prevent perpetual diff
          # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
          security_context {
            run_as_non_root = true
            allow_privilege_escalation = false
            privileged                 = false
            read_only_root_filesystem  = false

            capabilities {
              add  = []
              drop = ["NET_RAW"]
            }
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

              # Necessary to prevent perpetual diff
              # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
              "ephemeral-storage" = "1Gi"
            }
          }

          # Necessary to prevent perpetual diff
          # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
          security_context {
            run_as_non_root = true
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
            "${var.project_id}:${var.region}:${var.cloudsql_instance_id}",
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
