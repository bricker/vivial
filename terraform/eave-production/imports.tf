# import {
#   to = google_sql_database_instance.eave_pg_core
#   id = "eave-pg-core"
# }

# import {
#   to = module.gcp_monitoring.google_monitoring_alert_policy.ssl_certs_expiring
#   id = "projects/eave-production/alertPolicies/3320368542008647591"
# }

# import {
#   to = module.gcp_memorystore.google_monitoring_alert_policy.redis_memory_usage
#   id = "projects/eave-production/alertPolicies/1944058242697345118"
# }

# import {
#   to = module.gcp_memorystore.google_monitoring_alert_policy.redis_cpu_usage
#   id = "projects/eave-production/alertPolicies/8909395102126998152"
# }

# import {
#   to = google_monitoring_notification_channel.bcr_mobile
#   id = "projects/eave-production/notificationChannels/18048082649449908319"
# }

# import {
#   to = module.gcp_monitoring.google_monitoring_notification_channel.slack
#   id = "projects/eave-production/notificationChannels/12949516158598639712"
# }

# import {
#   to = google_compute_ssl_certificate.default
#   id = "projects/eave-production/global/sslCertificates/cert-subdomains-3"
# }
