output "gsa_account_id" {
  value = google_service_account.app_service_account.account_id
}

output "google_service_account" {
  value = google_service_account.app_service_account
}

output "ksa_name" {
  value = kubernetes_service_account.app_ksa.metadata[0].name
}
