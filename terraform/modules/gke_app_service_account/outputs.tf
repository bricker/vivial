output "gsa_ref" {
  value = google_service_account.app_service_account.account_id
}

output "ksa_name" {
  value = kubernetes_service_account.app_ksa.metadata[0].name
}
