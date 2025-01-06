module "app_gateway" {
  depends_on                                 = [google_compute_global_address.a_addrs]
  source                                     = "../../modules/app_gateway"
  name                                       = local.app_name
  kubernetes_namespace_name                  = var.kube_namespace_name
  google_certificate_manager_certificate_map = var.google_certificate_manager_certificate_map
  google_compute_ssl_policy                  = var.google_compute_ssl_policy
  google_compute_global_addresses            = google_compute_global_address.a_addrs
}

module "http_route_filters" {
  source = "../../modules/http_route_filters"
}

resource "kubernetes_manifest" "app_httproute" {
  lifecycle {
    prevent_destroy = true
  }

  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1beta1"
    kind       = "HTTPRoute"
    metadata = {
      name      = local.app_name
      namespace = var.kube_namespace_name
    }

    spec = {
      parentRefs = [
        {
          name = module.app_gateway.name
        }
      ]

      hostnames = [
        local.domain
      ]

      rules = [
        {
          # No path matching is specified, so all traffic is routed to this backend.
          backendRefs = [
            {
              name = module.kubernetes_service.kubernetes_service.name
              port = module.kubernetes_service.kubernetes_service.port.number
            }
          ]

          filters = [
            module.http_route_filters.request_header_modifier_standard,
            module.http_route_filters.response_header_modifier_standard,
          ]
        }
      ]
    }
  }
}
