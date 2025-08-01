resource "google_pubsub_topic" "eave_dead_letter_pubsub_topic" {
  kms_key_name               = null
  labels                     = {}
  message_retention_duration = "604800s"
  name                       = "eave_dead_letter"
  project                    = var.project_id
  timeouts {
    create = null
    delete = null
    update = null
  }
}

resource "google_pubsub_topic" "eave_event_pubsub_topic" {
  kms_key_name               = null
  labels                     = {}
  message_retention_duration = null
  name                       = "eave_event"
  project                    = var.project_id
  schema_settings {
    encoding = "BINARY"
    schema   = "projects/${var.project_id}/schemas/eave_event"
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}

resource "google_pubsub_topic" "gpt_request_event_pubsub_topic" {
  kms_key_name               = null
  labels                     = {}
  message_retention_duration = null
  name                       = "gpt_request_event"
  project                    = var.project_id
  schema_settings {
    encoding = "BINARY"
    schema   = "projects/${var.project_id}/schemas/gpt_request_event"
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
