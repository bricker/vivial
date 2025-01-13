output "name" {
  value = kubernetes_manifest.gateway.manifest.metadata.name
}
