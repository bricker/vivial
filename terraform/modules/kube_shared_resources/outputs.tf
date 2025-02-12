output "eave_namespace_name" {
  value = kubernetes_namespace.eave.metadata[0].name
}

output "shared_config_map_name" {
  value = kubernetes_config_map.shared.metadata[0].name
}
