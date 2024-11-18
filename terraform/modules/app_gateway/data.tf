data "google_compute_global_address" "given" {
  for_each = var.global_address_names
  name     = each.value
}
