output "router" {
  value = google_compute_router.cloud_nat_router
}

output "nat" {
  value = google_compute_router_nat.cloud_nat
}