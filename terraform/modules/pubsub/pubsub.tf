// https://registry.terraform.io/modules/terraform-google-modules/pubsub/google/latest

resource "google_pubsub_schema" "eave_event" {
  definition = null
  name       = "eave_event"
  project    = "eavefyi-dev"
  type       = "PROTOCOL_BUFFER"
  timeouts {
    create = null
    delete = null
  }
}


resource "google_pubsub_topic" "eave_event" {
  kms_key_name               = null
  labels                     = {}
  message_retention_duration = "604800s"
  name                       = "eave_event"
  project                    = "eavefyi-dev"
  schema_settings {
    encoding = "BINARY"
    schema   = "projects/eavefyi-dev/schemas/eave_event"
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}

resource "google_pubsub_subscription" "eave_event_bq_writer" {
  ack_deadline_seconds         = 10
  enable_exactly_once_delivery = false
  enable_message_ordering      = false
  filter                       = null
  labels                       = {}
  message_retention_duration   = "604800s"
  name                         = "eave_event_bq_writer_3"
  project                      = "eavefyi-dev"
  retain_acked_messages        = false
  topic                        = "projects/eavefyi-dev/topics/eave_event"
  bigquery_config {
    drop_unknown_fields = true
    table               = "eavefyi-dev.eave_events.eave_events"
    use_topic_schema    = true
    write_metadata      = true
  }
  dead_letter_policy {
    dead_letter_topic     = "projects/eavefyi-dev/topics/eave_dead_letter"
    max_delivery_attempts = 5
  }
  expiration_policy {
    ttl = ""
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}
