variable "google_project" {
  type=object({
    project_id = string
  })
}
variable "iap_oauth_client_secret" {
  type      = string
  sensitive = true
}

variable "dns_domain" {
  type = string
}

variable "www_public_domain_prefix" {
  type = string
}

variable "api_public_domain_prefix" {
  type = string
}

variable "admin_public_domain_prefix" {
  type = string
}

variable "STRIPE_ENVIRONMENT" {
  type = string
}

variable "EAVE_ENV" {
  type = string
  validation {
    condition     = contains(["production", "staging"], var.EAVE_ENV)
    error_message = "EAVE_ENV must be one of production, staging"
  }
}
