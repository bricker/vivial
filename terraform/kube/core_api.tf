locals {
  service_name = "core-api"
  app_name = "${local.service_name}-app"

  http_port = {
    name = "http"
    number = 80
  }

  app_port = {
    name = "app"
    number = 8000
  }

  clousql_proxy_healthcheck_port = {
    name = "healthcheck"
    number = 9090
  }

  cloudsql_proxy_port = {
    name = "proxy"
    number = 5432
  }

  cloudsql_proxy_version = "latest"
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

variable "db_user" {
  type=string
}

variable "domain" {
  type=string
}

variable "shared_config_map_name" {
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

variable "gsa_email" {
  type=string
}


resource "kubernetes_config_map" "core_api" {
  metadata {
    name = "${local.service_name}-configmap"
    namespace = var.namespace
  }

  data = {
    GAE_SERVICE = local.service_name
    GAE_VERSION = var.release_version
    GAE_RELEASE_DATE = var.release_date
    LOG_LEVEL = var.LOG_LEVEL
  }
}

resource "kubernetes_secret" "core_api" {
  metadata {
    name = "${local.service_name}-secret"
    namespace = var.namespace
  }

  type = "Opaque"
  data = {
  }
}

resource "kubernetes_manifest" "core_api_managed_certificate" {
  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "ManagedCertificate"
    metadata = {
      name = "${local.service_name}-cert"
      namespace = var.namespace
    }

    spec = {
      domains = [var.domain]
    }
  }
}

resource "kubernetes_service_account" "core_api" {
  metadata {
    name = "ksa-app-${local.service_name}"
    namespace = var.namespace
    annotations = {
      "iam.gke.io/gcp-service-account" = var.gsa_email
    }
  }
}

output "kubernetes_service_account_core_api_name" {
  value = kubernetes_service_account.core_api.metadata.0.name
}

resource "kubernetes_service" "core_api" {
  metadata {
    name = local.service_name
    namespace = var.namespace
    annotations = {
      "beta.cloud.google.com/backend-config" = jsonencode({"default": var.shared_backend_config_name})
    }

    labels = {
      app = local.app_name
    }
  }

  spec {
    selector = {
      app = local.app_name
    }

    type = "NodePort"
    port {
      name = local.http_port.name
      protocol = "TCP"
      port = local.http_port.number
      target_port = local.app_port.name
    }
  }
}

resource "kubernetes_ingress_v1" "core_api" {
  metadata {
    name = "${local.service_name}-ingress"
    namespace = var.namespace
    annotations = {
      "networking.gke.io/v1beta1.FrontendConfig" = kubernetes_manifest.shared_frontend_config.manifest.metadata.name
      "networking.gke.io/managed-certificates" = kubernetes_manifest.core_api_managed_certificate.manifest.metadata.name
      "kubernetes.io/ingress.global-static-ip-name" = var.static_ip_name
      "kubernetes.io/ingress.class" = "gce"
    }

    labels = {
      app = local.app_name
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
                name = local.http_port.name
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
                name = local.http_port.name
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
                name = local.http_port.name
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
                name = local.http_port.name
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
    name = "${local.service_name}-deployment"
    namespace = var.namespace
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
        labels = {
          app = local.app_name
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
          name = local.service_name
          image = "${var.docker_repository.location}-docker.pkg.dev/${var.docker_repository.project}/${var.docker_repository.repository_id}/${local.service_name}:${var.release.version}"

          port {
            name = local.app_port.name
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
              name = var.shared_config_map_name
            }
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.core_api.metadata.0.name
            }
          }

          env {
            name = "EAVE_DB_NAME"
            value = var.db_name
          }
          env {
            name = "EAVE_DB_USER"
            value = var.db_user
          }
          env {
            name = "EAVE_DB_HOST"
            value = "127.0.0.1"
          }
          env {
            name = "EAVE_DB_PORT"
            value = "${local.cloudsql_proxy_port.number}"
          }
          env {
            name = "GUNICORN_CMD_ARGS"
            value = "--bind=0.0.0.0:${local.app_port.number} --workers=3 --timeout=90"
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
              port = local.app_port.name
            }
          }

          liveness_probe {
            failure_threshold = 5
            http_get {
              path = "/status"
              port = local.app_port.name
            }
          }
        }

        container {
          name = "cloud-sql-proxy"
          image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:${local.cloudsql_proxy_version}"

          port {
            name = local.clousql_proxy_healthcheck_port.name
            container_port = local.clousql_proxy_healthcheck_port.number
          }

          port {
            name = local.cloudsql_proxy_port.name
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
            "${var.project_id}:${var.region}:${var.cloudsql_instance_id}",
          ]

          startup_probe {
            period_seconds = 1
            timeout_seconds = 5
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
            period_seconds = 60
            timeout_seconds = 30
            failure_threshold = 5
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
