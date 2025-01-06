# resource "kubernetes_manifest" "eventbrite_filler_cron" {
#   manifest = {
#     apiVersion = "batch/v1beta1"
#     kind       = "CronJob"

#     metadata = {
#       name      = local.eventbrite_filler_job_name
#       namespace = var.kube_namespace_name
#     }

#     spec = {
#       concurrencyPolicy = "Replace"
#       schedule          = "0 20 * * *"
#       timezone          = "Etc/UTC"

#       jobTemplate = {
#         metadata = {
#           name = local.eventbrite_filler_job_name
#         }

#         spec = {
#           template = {
#             metadata = {
#               name = local.eventbrite_filler_job_name
#             }

#             spec = {
#               serviceAccountName = module.service_accounts.ksa_name
#               restartPolicy      = "OnFailure"

#               # Necessary to prevent perpetual diff
#               # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
#               toleration = {
#                 effect   = "NoSchedule"
#                 key      = "kubernetes.io/arch"
#                 operator = "Equal"
#                 value    = "amd64"
#               }

#               # Necessary to prevent perpetual diff
#               # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
#               securityContext = {
#                 runAsNonRoot = true

#                 seccompProfile = {
#                   type = "RuntimeDefault"
#                 }
#               }

#               containers = [
#                 {
#                   name  = local.app_name
#                   image = "${data.google_artifact_registry_repository.docker.location}-docker.pkg.dev/${data.google_artifact_registry_repository.docker.project}/${data.google_artifact_registry_repository.docker.repository_id}/${local.app_name}:${var.release_version}"

#                   resources = {
#                     # requests and limits must always be the same on Autopilot clusters without bursting.
#                     # if requests is omitted, the limits values are used.
#                     limits = {
#                       cpu    = "250m"
#                       memory = "1Gi"
#                       # Necessary to prevent perpetual diff
#                       # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
#                       "ephemeral-storage" = "1Gi"
#                     }
#                   }

#                   envFrom = {
#                     secretRef = {
#                       name = kubernetes_secret.app.metadata[0].name
#                     }
#                   }
#                   envFrom = {
#                     configMapRef = {
#                       name = var.shared_config_map_name
#                     }
#                   }
#                   envFrom = {
#                     configMapRef = {
#                       name = kubernetes_config_map.app.metadata[0].name
#                     }
#                   }

#                   env = {
#                     name  = "EAVE_DB_NAME"
#                     value = google_sql_database.app.name
#                   }
#                   env = {
#                     name  = "EAVE_DB_USER"
#                     value = google_sql_user.app.name
#                   }
#                   env = {
#                     name  = "EAVE_DB_HOST"
#                     value = "127.0.0.1"
#                   }
#                   env = {
#                     name  = "EAVE_DB_PORT"
#                     value = local.cloudsql_proxy_port.number
#                   }

#                   command = ["python", "-m", "eave/core/eventbrite_filler.py"]

#                   # Necessary to prevent perpetual diff
#                   # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
#                   securityContext = {
#                     runAsNonRoot             = true
#                     allowPrivilegeEscalation = false
#                     privileged               = false
#                     readOnlyRootFilesystem   = false

#                     capabilities = {
#                       add  = []
#                       drop = ["NET_RAW"]
#                     }
#                   }
#                 },
#               ]

#               initContainers = [
#                 {
#                   name  = "cloud-sql-proxy"
#                   image = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:${local.cloudsql_proxy_version}"

#                   restartPolicy = "Always"

#                   port = {
#                     name          = local.clousql_proxy_healthcheck_port.name
#                     containerPort = local.clousql_proxy_healthcheck_port.number
#                   }

#                   port = {
#                     name          = local.cloudsql_proxy_port.name
#                     containerPort = local.cloudsql_proxy_port.number
#                   }

#                   resources = {
#                     # requests and limits must always be the same on Autopilot clusters without bursting.
#                     # if requests is omitted, the limits values are used.
#                     limits = {
#                       cpu    = "500m"
#                       memory = "2Gi"

#                       # Necessary to prevent perpetual diff
#                       # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
#                       "ephemeral-storage" = "1Gi"
#                     }
#                   }

#                   # Necessary to prevent perpetual diff
#                   # https://github.com/hashicorp/terraform-provider-kubernetes/pull/2380
#                   securityContext = {
#                     runAsNonRoot             = true
#                     allowPrivilegeEscalation = false
#                     privileged               = false
#                     readOnlyRootFilesystem   = false

#                     capabilities = {
#                       add  = []
#                       drop = ["NET_RAW"]
#                     }
#                   }

#                   args = [
#                     # Enable healthcheck endpoints for kube probes
#                     "--health-check",
#                     "--http-address=0.0.0.0",                                     # Bind to all interfaces so that the Kubernetes control plane can communicate with this process.
#                     "--http-port=${local.clousql_proxy_healthcheck_port.number}", # This is the default

#                     # If connecting from a VPC-native GKE cluster, you can use the
#                     # following flag to have the proxy connect over private IP
#                     "--private-ip",

#                     # If you are not connecting with Automatic IAM, you can delete
#                     # the following flag.
#                     "--auto-iam-authn",

#                     # tcp should be set to the port the proxy should listen on
#                     # and should match the DB_PORT value set above.
#                     # Defaults: MySQL: 3306, Postgres: 5432, SQLServer: 1433
#                     "--port=${local.cloudsql_proxy_port.number}",
#                     "--structured-logs",
#                     # - "--unix-socket /cloudsql"
#                     var.google_sql_database_instance.connection_name,
#                   ]

#                   startupProbe = {
#                     periodSeconds    = 1
#                     timeoutSeconds   = 5
#                     failureThreshold = 20
#                     httpGet = {
#                       path = "/startup"
#                       port = local.clousql_proxy_healthcheck_port.name
#                     }
#                   }

#                   # The documentation does not recommend using the readiness probe.
#                   # The cloud-sql-proxy readiness probe checks for issues that can usually resolve themselves, so this check could restart the container unnecessarily.

#                   livenessProbe = {
#                     initialDelaySeconds = 0
#                     periodSeconds       = 60
#                     timeoutSeconds      = 30
#                     failureThreshold    = 5
#                     httpGet = {
#                       path = "/liveness"
#                       port = local.clousql_proxy_healthcheck_port.name
#                     }
#                   }
#                 }
#               ]
#             }
#           }
#         }
#       }
#     }
#   }
# }

resource "kubernetes_cron_job_v1" "eventbrite_filler" {
  metadata {
    name      = local.eventbrite_filler_job_name
    namespace = var.kube_namespace_name
  }

  spec {
    concurrency_policy = "Replace"
    schedule           = "0 12 * * *"

    job_template {
      metadata {
        name = local.eventbrite_filler_job_name
      }

      spec {
        template {
          metadata {
            name = local.eventbrite_filler_job_name
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

              command = ["python", "-m", "eave/core/eventbrite_filler.py"]

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
                var.google_sql_database_instance.connection_name,
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
  }
}