# These are individual variables instead of a single map+iteration so that all of the expected secrets are required to be set.
# If any of these aren't set, terraform apply won't run.
# Additionally, a map with `sensitive=true` can't be used for iteration.

variable "SLACK_SYSTEM_BOT_TOKEN" {
  type      = string
  sensitive = true
}

variable "GCP_MONITORING_SLACK_AUTH_TOKEN" {
  type      = string
  sensitive = true
}

variable "SENDGRID_API_KEY" {
  type      = string
  sensitive = true
}

variable "EVENTBRITE_API_KEY" {
  type      = string
  sensitive = true
}

variable "EVENTBRITE_API_KEYS" {
  type      = list(string)
  sensitive = true
}

variable "STRIPE_SECRET_KEY" {
  type      = string
  sensitive = true
}

variable "GOOGLE_MAPS_API_KEY" {
  type      = string
  sensitive = true
}
