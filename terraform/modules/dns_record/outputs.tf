output "records" {
  value = join(".", compact([var.domain_prefix, local.root_domain]))
}