# # https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api



resource "kubernetes_manifest" "gateway" {
  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "Gateway"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      # https://cloud.google.com/kubernetes-engine/docs/concepts/gateway-api#gatewayclass
      gatewayClassName = "gke-l7-global-external-managed"
      listeners = [
        {
          name = "https"
          protocol = "HTTPS"
          port = 443

          tls = {
            mode = "Terminate"
            options = {
              "networking.gke.io/pre-shared-certs" = kubernetes_manifest.managed_certificate.manifest.metadata.name
            }
          }

          allowedRoutes = {
            kinds = [
              {
                kind = "HTTPRoute"
              }
            ]
          }
        }
      ]

      addresses = [
        {
          type = "NamedAddress"
          value = google_compute_global_address.default.name
        }
      ]
    }
  }
}


# https://cloud.google.com/kubernetes-engine/docs/how-to/configure-gateway-resources#configure_ssl_policies
resource "kubernetes_manifest" "gateway_policy" {
  manifest = {
    apiVersion = "networking.gke.io/v1"
    kind       = "GCPGatewayPolicy"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      default = {
        sslPolicy = var.ssl_policy_name
      }

      targetRef = {
        group = "gateway.networking.k8s.io"
        kind = "Gateway"
        name = kubernetes_manifest.gateway.manifest.metadata.name
      }
    }
  }
}


resource "kubernetes_manifest" "api_httproute" {
  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "HTTPRoute"
    metadata = {
      name = local.app_name
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      parentRefs = [
        {
          name = kubernetes_manifest.gateway.manifest.metadata.name
        }
      ]

      hostname = [
        local.domain
      ]

      rules = [
        {
          matches = [
            {
              path = {
                type = "PathPrefix"
                value = ""
              }
            }
          ]

          backendRefs = [
            {
              name = kubernetes_service.app.metadata[0].name
              port = kubernetes_service.app.ports[0].http
            }
          ]

          filters = [
            {
              type = "URLRewrite"
              urlRewrite = {
                path = {
                  type = "ReplacePrefixMatch"
                  replacePrefixMatch = "/"
                }
              }
            },
            {
              type = "RequestHeaderModifier"
              requestHeaderModifier = {
                add = [
                  {
                    name = "eave-lb"
                    value = "1"
                  }
                ]
              }
            },
            {
              type = "ResponseHeaderModifier"
              responseHeaderModifier = {
                set = [
                  {
                    name = "server"
                    value = "n/a"
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  }
}

resource "kubernetes_manifest" "metabase_httproute" {
  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "HTTPRoute"
    metadata = {
      name = "metabase-rewrite"
      namespace = var.kube_namespace_name

      labels = {
        app = local.app_name
      }
    }

    spec = {
      parentRefs = [
        {
          name = kubernetes_manifest.gateway.manifest.metadata.name
        }
      ]

      hostname = [
        local.mbproxy_domain
      ]

      rules = [
        {
          matches = [
            {
              path = {
                type = "PathPrefix"
                value = "/"
              }
            }
          ]

          backendRefs = [
            {
              name = kubernetes_service.app.metadata[0].name
              port = kubernetes_service.app.ports[0].http
            }
          ]

          filters = [
            {
              type = "URLRewrite"
              urlRewrite = {
                path = {
                  type = "ReplacePrefixMatch"
                  replacePrefixMatch = "/_/mbproxy"
                }
              }
            },
            {
              type = "RequestHeaderModifier"
              requestHeaderModifier = {
                add = [
                  {
                    name = "eave-lb"
                    value = "1"
                  }
                ]
              }
            },
            {
              type = "ResponseHeaderModifier"
              responseHeaderModifier = {
                set = [
                  {
                    name = "server"
                    value = "n/a"
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  }
}