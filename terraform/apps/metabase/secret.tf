resource "kubernetes_secret" "shared" {
  metadata {
    name = "metabase-shared"
    namespace = var.kube_namespace_name
  }

  type = "Opaque"
  data = {
    MB_PREMIUM_EMBEDDING_TOKEN = var.MB_SHARED_SECRETS.MB_PREMIUM_EMBEDDING_TOKEN
    MB_EMAIL_SMTP_USERNAME = var.MB_SHARED_SECRETS.MB_EMAIL_SMTP_USERNAME
    MB_EMAIL_SMTP_PASSWORD = var.MB_SHARED_SECRETS.MB_EMAIL_SMTP_PASSWORD
  }
}