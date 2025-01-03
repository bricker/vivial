variable "public_domain_prefix" {
  type    = string
  default = "api"
}

variable "environment" {
  description = "Allowed values: DEV, STG, PROD"
  type        = string
  default     = "DEV"

  validation {
    condition     = contains(["DEV", "STG", "PROD"], var.environment)
    error_message = "Allowed values: DEV, STG, PROD"
  }
}

variable "google_dns_managed_zone" {
  type = object({
    name     = string
    dns_name = string
  })
}

variable "google_compute_network" {
  type = object({
    name = string
  })
}

variable "google_compute_subnetwork" {
  type = object({
    name = string
  })
}

variable "google_compute_ssl_policy" {
  type = object({
    name = string
  })
}

variable "google_certificate_manager_certificate_map" {
  type = object({
    id   = string
    name = string
  })
}

variable "google_sql_database_instance" {
  type = object({
    name            = string
    connection_name = string
  })
}

variable "google_kms_crypto_key_jws_signing_key" {
  type = object({
    id = string
  })
}

variable "docker_repository_ref" {
  type = object({
    location      = string
    repository_id = string
  })
}

variable "kube_namespace_name" {
  type = string
}

variable "shared_config_map_name" {
  type = string
}

variable "release_version" {
  type = string
}

variable "LOG_LEVEL" {
  type    = string
  default = "debug"
}

variable "impersonator_role_name" {
  type = string
}

variable "impersonators" {
  type    = list(string)
  default = []
}

variable "compute_oslogin_role_name" {
  type = string
}

variable "service_account_user_role_name" {
  type = string
}

variable "bastion_accessors" {
  type    = list(string)
  default = []
}

variable "JWS_SIGNING_KEY_VERSION_PATH" {
  type = string
}

variable "iap_enabled" {
  type    = bool
}

variable "iap_oauth_client_id" {
  type     = string
}

variable "iap_oauth_client_kube_secret_name" {
  type     = string
}

variable "iap_jwt_aud" {
  type=string
}
