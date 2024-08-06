# These are individual variables instead of a single map+iteration so that all of the expected secrets are required to be set.
# If any of these aren't set, terraform apply won't run.
# Additionally, a map with `sensitive=true` can't be used for iteration.


variable "INTERNAL_EAVE_CREDENTIALS" {
  type = object({
    SERVER_CREDENTIALS = string,
    CLIENT_ID          = string,
  })
  sensitive = true
}

variable "OPENAI_API_KEY" {
  type      = string
  sensitive = true
}

variable "EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64" {
  type      = string
  sensitive = true
}

variable "SLACK_SYSTEM_BOT_TOKEN" {
  type      = string
  sensitive = true
}

variable "IAP_OAUTH_CLIENT_ID" {
  type=string
}

variable "IAP_OAUTH_CLIENT_SECRET" {
  type=string
  sensitive=true
}