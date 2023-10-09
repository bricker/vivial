resource "google_pubsub_subscription" "eave_dead_letter_pubsub_subscription" {
  depends_on = [ google_pubsub_topic.eave_dead_letter_pubsub_topic ]

  ack_deadline_seconds         = 10
  enable_exactly_once_delivery = false
  enable_message_ordering      = false
  filter                       = null
  labels                       = {}
  message_retention_duration   = "604800s"
  name                         = "eave_dead_letter"
  project                      = var.project_id
  retain_acked_messages        = false
  topic                        = google_pubsub_topic.eave_dead_letter_pubsub_topic.id
  expiration_policy {
    ttl = ""
  }
  timeouts {
    create = null
    delete = null
    update = null
  }
}

resource "google_pubsub_subscription" "eave_event_bq_writer_pubsub_subscription" {
  depends_on = [
    google_pubsub_topic.eave_dead_letter_pubsub_topic,
    google_pubsub_topic.eave_event_pubsub_topic
  ]

  ack_deadline_seconds         = 10
  enable_exactly_once_delivery = false
  enable_message_ordering      = false
  filter                       = null
  labels                       = {}
  message_retention_duration   = "604800s"
  name                         = "eave_event_bq_writer"
  project                      = var.project_id
  retain_acked_messages        = false
  topic                        = google_pubsub_topic.eave_event_pubsub_topic.id
  bigquery_config {
    drop_unknown_fields = true
    table               = "${var.project_id}.eave_events.eave_events"
    use_topic_schema    = true
    write_metadata      = true
  }
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.eave_dead_letter_pubsub_topic.id
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

resource "google_pubsub_subscription" "gpt_request_event_bq_writer_pubsub_subscription" {
  depends_on = [
    google_pubsub_topic.eave_dead_letter_pubsub_topic,
    google_pubsub_topic.gpt_request_event_pubsub_topic
  ]

  ack_deadline_seconds         = 10
  enable_exactly_once_delivery = false
  enable_message_ordering      = false
  filter                       = null
  labels                       = {}
  message_retention_duration   = "604800s"
  name                         = "gpt_request_event_bq_writer"
  project                      = var.project_id
  retain_acked_messages        = false
  topic                        = google_pubsub_topic.gpt_request_event_pubsub_topic.id
  bigquery_config {
    drop_unknown_fields = true
    table               = "${var.project_id}.eave_events.gpt_request_events"
    use_topic_schema    = true
    write_metadata      = true
  }
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.eave_dead_letter_pubsub_topic.id
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