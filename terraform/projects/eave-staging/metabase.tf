locals {
  metabase_instances = {
    "dev": {
    }
  }
}

resource "kubernetes_namespace" "metabase" {
  metadata {
    name = "metabase"
  }
}

module "metabase_role" {
  source      = "../../modules/custom_role"
  role_id     = "eave.metabaseApp"
  title       = "Metabase App"
  description = "Permissions needed by the Metabase apps"
  base_roles  = [
    "roles/logging.logWriter",
    "roles/cloudsql.instanceUser", # for IAM auth
    "roles/cloudsql.client",
  ]
}

# Create app service accounts
module "metabase_service_accounts" {
  for_each = local.metabase_instances

  source         = "../../modules/gke_app_service_account"
  project_id     = local.project_id
  app            = "metabase-${each.key}"
  kube_namespace = kubernetes_namespace.metabase.metadata.0.name
}

# Bind the custom roles to necessary service accounts. This is authoritative.
resource "google_project_iam_binding" "metabase_role_bindings" {
  project = local.project_id
  role    = module.metabase_role.role.id

  members = [
    for key, sa in module.metabase_service_accounts :
    "serviceAccount:${sa.gsa.email}"
  ]
}


resource "kubernetes_config_map" "metabase_shared" {
  metadata {
    name = "metabase-shared-configmap"
    namespace = kubernetes_namespace.metabase.metadata.0.name
  }

  data = {
    # MB_NO_SURVEYS: "true"
    # MB_SHOW_HOMEPAGE_DATA: "false"
    # MB_SHOW_HOMEPAGE_XRAYS: "false"
    # MB_SHOW_DATABASE_SYNCING_MODAL: "false"
    # MB_LOAD_ANALYTICS_CONTENT: "false"
    # MB_COLORIZE_LOGS: "false"
    # MB_EMOJI_IN_LOGS: "false"
    # MB_SITE_NAME: TKTK Eave Staging Site
    # MB_SITE_URL: "https://metabase.${EAVE_ROOT_DOMAIN}"
    # MB_ANON_TRACKING_ENABLED: "false"
    # MB_ENABLE_XRAYS: "true"
    # MB_ENABLE_NESTED_QUERIES: "true"
    # MB_CHECK_FOR_UPDATES: "false"
    # MB_EMAIL_SMTP_HOST: smtp-relay.gmail.com
    # MB_EMAIL_SMTP_PORT: "587"
    # MB_EMAIL_SMTP_SECURITY: tls
    # MB_EMAIL_FROM_ADDRESS: info@eave.fyi
    # MB_EMAIL_FROM_NAME: Eave
    # MB_ADMIN_EMAIL: support@eave.fyi
    # MB_SEND_EMAIL_ON_FIRST_LOGIN_FROM_NEW_DEVICE: "false"
    # # MB_EMAIL_REPLY_TO: "\"['info@eave.fyi']\""
    # # MB_SLACK_APP_TOKEN:
    # # MB_SLACK_FILES_CHANNEL:
    # MB_ENABLE_PASSWORD_LOGIN: "true" # for Eave admins
    # MB_SEND_NEW_SSO_USER_ADMIN_EMAIL: "true"
    # # MB_SESSION_TIMEOUT:
    # # MB_MAP_TILE_SERVER_URL:
    # MB_REPORT_TIMEZONE: America/Los_Angeles # FIXME: Can the browser's timezone be used?
    # MB_ENABLE_PUBLIC_SHARING: "false"
    # MB_ENABLE_EMBEDDING: "true"
    # MB_EMBEDDING_APP_ORIGIN: "dashboard.${EAVE_ROOT_DOMAIN}"
    # MB_SESSION_COOKIE_SAMESITE: lax
    # MB_JWT_ENABLED: "true"
    # MB_JWT_IDENTITY_PROVIDER_URI: "https://dashboard.${EAVE_ROOT_DOMAIN}/login"
    # MB_ENABLE_QUERY_CACHING: "false"
    # MB_PERSISTED_MODELS_ENABLED: "false"
    # MB_PERSISTED_MODEL_REFRESH_CRON_SCHEDULE: ""
    # MB_APPLICATION_NAME: TKTK Eave Staging Application
    # # MB_APPLICATION_FONT:
    # # MB_APPLICATION_COLORS:
    # # MB_APPLICATION_LOGO_URL:
    # # MB_APPLICATION_FAVICON_URL:
    # # MB_LANDING_PAGE:
    # MB_LOADING_MESSAGE: running-query # This is an enum, not an arbitrary string. Setting it to an unsupported value breaks the UI!
    # MB_SHOW_METABOT: "false"
    # MB_SHOW_LIGHTHOUSE_ILLUSTRATION: "false"
  }
}

resource "kubernetes_config_map" "metabase_instances" {
  for_each = local.metabase_instances

  metadata {
    name = "metabase-${each.key}-configmap"
    namespace = kubernetes_namespace.metabase.metadata.0.name
  }

  data = {
    # MB_DB_DBNAME: metabase
    # MB_NO_SURVEYS: "true"
    # MB_SHOW_HOMEPAGE_DATA: "false"
    # MB_SHOW_HOMEPAGE_XRAYS: "false"
    # MB_SHOW_DATABASE_SYNCING_MODAL: "false"
    # MB_LOAD_ANALYTICS_CONTENT: "false"
    # MB_COLORIZE_LOGS: "false"
    # MB_EMOJI_IN_LOGS: "false"
    # MB_SITE_NAME: TKTK Eave Staging Site
    # MB_SITE_URL: "https://metabase.${EAVE_ROOT_DOMAIN}"
    # MB_ANON_TRACKING_ENABLED: "false"
    # MB_ENABLE_XRAYS: "true"
    # MB_ENABLE_NESTED_QUERIES: "true"
    # MB_CHECK_FOR_UPDATES: "false"
    # MB_EMAIL_SMTP_HOST: smtp-relay.gmail.com
    # MB_EMAIL_SMTP_PORT: "587"
    # MB_EMAIL_SMTP_SECURITY: tls
    # MB_EMAIL_FROM_ADDRESS: info@eave.fyi
    # MB_EMAIL_FROM_NAME: Eave
    # MB_ADMIN_EMAIL: support@eave.fyi
    # MB_SEND_EMAIL_ON_FIRST_LOGIN_FROM_NEW_DEVICE: "false"
    # # MB_EMAIL_REPLY_TO: "\"['info@eave.fyi']\""
    # # MB_SLACK_APP_TOKEN:
    # # MB_SLACK_FILES_CHANNEL:
    # MB_ENABLE_PASSWORD_LOGIN: "true" # for Eave admins
    # MB_SEND_NEW_SSO_USER_ADMIN_EMAIL: "true"
    # # MB_SESSION_TIMEOUT:
    # # MB_MAP_TILE_SERVER_URL:
    # MB_REPORT_TIMEZONE: America/Los_Angeles # FIXME: Can the browser's timezone be used?
    # MB_ENABLE_PUBLIC_SHARING: "false"
    # MB_ENABLE_EMBEDDING: "true"
    # MB_EMBEDDING_APP_ORIGIN: "dashboard.${EAVE_ROOT_DOMAIN}"
    # MB_SESSION_COOKIE_SAMESITE: lax
    # MB_JWT_ENABLED: "true"
    # MB_JWT_IDENTITY_PROVIDER_URI: "https://dashboard.${EAVE_ROOT_DOMAIN}/login"
    # MB_ENABLE_QUERY_CACHING: "false"
    # MB_PERSISTED_MODELS_ENABLED: "false"
    # MB_PERSISTED_MODEL_REFRESH_CRON_SCHEDULE: ""
    # MB_APPLICATION_NAME: TKTK Eave Staging Application
    # # MB_APPLICATION_FONT:
    # # MB_APPLICATION_COLORS:
    # # MB_APPLICATION_LOGO_URL:
    # # MB_APPLICATION_FAVICON_URL:
    # # MB_LANDING_PAGE:
    # MB_LOADING_MESSAGE: running-query # This is an enum, not an arbitrary string. Setting it to an unsupported value breaks the UI!
    # MB_SHOW_METABOT: "false"
    # MB_SHOW_LIGHTHOUSE_ILLUSTRATION: "false"
  }
}

resource "kubernetes_secret" "metabase_shared" {
  metadata {
    name = "metabase-shared-secret"
    namespace = kubernetes_namespace.metabase.metadata.0.name
  }

  type = "Opaque"
  data = {
    # MB_ENCRYPTION_SECRET_KEY: "${MB_ENCRYPTION_SECRET_KEY}"
    # MB_PREMIUM_EMBEDDING_TOKEN: "${MB_PREMIUM_EMBEDDING_TOKEN}"
    # MB_EMAIL_SMTP_USERNAME: "${MB_EMAIL_SMTP_USERNAME}"
    # MB_EMAIL_SMTP_PASSWORD: "${MB_EMAIL_SMTP_PASSWORD}"
    # MB_JWT_SHARED_SECRET: "${MB_JWT_SHARED_SECRET}"
  }
}

resource "kubernetes_secret" "metabase_instances" {
  for_each = local.metabase_instances

  metadata {
    name = "metabase-${each.key}-secret"
    namespace = kubernetes_namespace.metabase.metadata.0.name
  }

  type = "Opaque"
  data = {
    # MB_ENCRYPTION_SECRET_KEY: "${MB_ENCRYPTION_SECRET_KEY}"
    # MB_PREMIUM_EMBEDDING_TOKEN: "${MB_PREMIUM_EMBEDDING_TOKEN}"
    # MB_EMAIL_SMTP_USERNAME: "${MB_EMAIL_SMTP_USERNAME}"
    # MB_EMAIL_SMTP_PASSWORD: "${MB_EMAIL_SMTP_PASSWORD}"
    # MB_JWT_SHARED_SECRET: "${MB_JWT_SHARED_SECRET}"
  }
}

resource "kubernetes_manifest" "metabase_shared_backend_config" {
  manifest = {
    apiVersion = "cloud.google.com/v1"
    kind       = "BackendConfig"
    metadata = {
      name = "metabase-shared-bc"
      namespace = kubernetes_namespace.metabase.metadata.0.name
    }

    spec = {
      healthCheck = {
        type = "HTTP"
        requestPath = "/api/health"
        port = 3000
        checkIntervalSec = 30
        unhealthyThreshold = 4
      }

      logging = {
        enable = true
        sampleRate = 0.5
      }

      customResponseHeaders = {
        headers = [
          "server: n/a"
        ]
      }
    }
  }
}

resource "kubernetes_service" "metabase_instances" {
  for_each = local.metabase_instances

  metadata {
    name = "metabase-${each.key}"
    namespace = kubernetes_namespace.metabase.metadata.0.name
    annotations = {
      "beta.cloud.google.com/backend-config" = "{\"default\": \"${kubernetes_manifest.metabase_shared_backend_config.manifest.metadata.name}\"}"
    }
  }

  spec {
    selector = {
      "app" = "metabase-${each.key}-app"
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

resource "kubernetes_deployment" "metabase" {
  for_each = local.metabase_instances
  wait_for_rollout = false

  metadata {
    name = "metabase-${each.key}-deployment"
    namespace = kubernetes_namespace.metabase.metadata.0.name
    labels = {
      app = "metabase-${each.key}-app"
    }
  }

  spec {
    selector {
      match_labels = {
        app = "metabase-${each.key}-app"
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
          app = "metabase-${each.key}-app"
        }
      }
      spec {
        service_account_name = metabase_service_accounts.kubernetes_service_account.metabase.metadata.0.name

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
          name = "metabase-enterprise"
          image = "metabase/metabase-enterprise:latest"

          port {
            name = "app"
            container_port = 3000
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
              name = kubernetes_secret.metabase.metadata.0.name
            }
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.metabase.metadata.0.name
            }
          }

          env {
            name = "MB_DB_USER"
            value = "gsa-app-metabase-${var.metabase_instance_id}@${var.project_id}.iam"
          }
          env {
            name = "MB_DB_TYPE"
            value = "postgres"
          }
          env {
            name = "MB_DB_HOST"
            value = "127.0.0.1"
          }
          env {
            name = "MB_DB_PORT"
            value = "5432"
          }
          env {
            name = "MB_JETTY_HOST"
            value = "0.0.0.0" # Default for Docker
          }
          env {
            name = "MB_JETTY_PORT"
            value = "3000" # Default
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

          liveness_probe {
            period_seconds = 60
            timeout_seconds = 30
            failure_threshold = 5
            http_get {
              path = "/api/health"
              port = "app"
            }
          }

          startup_probe {
            # The metabase container takes a long time to boot up
            period_seconds = 10
            failure_threshold = 30
            http_get {
              path = "/api/health"
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
