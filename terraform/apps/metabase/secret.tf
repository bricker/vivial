resource "kubernetes_secret" "shared" {
  metadata {
    name      = "metabase-shared"
    namespace = var.kube_namespace_name
  }

  type = "Opaque"
  data = {
    MB_PREMIUM_EMBEDDING_TOKEN = var.MB_SHARED_SECRETS.MB_PREMIUM_EMBEDDING_TOKEN
    MB_EMAIL_SMTP_USERNAME     = var.MB_SHARED_SECRETS.MB_EMAIL_SMTP_USERNAME
    MB_EMAIL_SMTP_PASSWORD     = var.MB_SHARED_SECRETS.MB_EMAIL_SMTP_PASSWORD
  }
}

# Individual instance secrets
resource "kubernetes_secret" "instances" {
  for_each = var.metabase_instances

  metadata {
    name      = "mb-${each.value.metabase_instance_id}"
    namespace = var.kube_namespace_name

    labels = {
      app = "mb-${each.value.metabase_instance_id}"
    }
  }

  type = "Opaque"
  data = {
    MB_ENCRYPTION_SECRET_KEY = var.MB_INSTANCE_SECRETS[each.key].MB_ENCRYPTION_SECRET_KEY
    MB_JWT_SHARED_SECRET     = var.MB_INSTANCE_SECRETS[each.key].MB_JWT_SHARED_SECRET
  }
}