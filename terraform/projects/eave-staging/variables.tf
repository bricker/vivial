variable "METABASE_UI_BIGQUERY_ACCESSOR_GSA_KEY_JSON_B64" {
  type=string
  sensitive=true
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
