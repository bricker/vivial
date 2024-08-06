output "eave_namespace_name" {
  value = kubernetes_namespace.eave.metadata[0].name
}

output "shared_config_map_name" {
  value = kubernetes_config_map.shared.metadata[0].name
}

output "iap_oauth_client_kube_secret_name" {
  # This value should be the same for all namespaces, so we'll just grab the first one.
  value = kubernetes_secret.iap_oauth_client_secret[kubernetes_namespace.eave.metadata[0].name].metadata[0].name
}