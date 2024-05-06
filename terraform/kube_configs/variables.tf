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
    project=string
    location=string
  })
}

variable "METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64" {
  type=string
  sensitive = true
}

variable "RELEASE" {
  type=object({
    core_api=object({
      version=string
      release_date=string
    })
    dashboard=object({
      version=string
      release_date=string
    })
    playground_todoapp=object({
      version=string
      release_date=string
    })
  })
}

variable "static_ip_names" {
  type=object({
    core_api=string
    dashboard=string
    playground_todoapp=string
  })
}