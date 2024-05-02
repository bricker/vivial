variable "project_id" {
  type=string
}

variable "region" {
  type=string
}

variable "root_domain" {
  type=string
}

variable "docker_repository" {
  type = object({
    repository_id=string
  })
}

variable "METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64" {
  type=string
  sensitive = true
}