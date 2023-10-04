resource "google_pubsub_schema" "eave_event_schema_pubsub_schema" {
  definition = "syntax = \"proto3\";\n\nmessage EaveEvent {\n  string event_name = 1;\n  string event_description = 2;\n  float event_ts = 5;\n  string event_source = 6;\n  string opaque_params = 3;\n  string eave_account_id = 4;\n  string eave_visitor_id = 7;\n  string eave_team_id = 8;\n  string eave_env = 9;\n  string opaque_eave_ctx = 10;\n  string eave_account = 11;\n  string eave_team = 12;\n}"
  name       = "eave_event_schema"
  project    = var.project_id
  type       = "PROTOCOL_BUFFER"
  timeouts {
    create = null
    delete = null
  }
}

resource "google_pubsub_schema" "eave_event_pubsub_schema" {
  definition = "syntax = \"proto3\";\n\nmessage EaveEvent {\n  string event_name = 1;\n  string event_time = 3;\n  optional string event_description = 2;\n  optional string event_source = 4;\n  optional string opaque_params = 5;\n  optional string eave_account_id = 6;\n  optional string eave_visitor_id = 7;\n  optional string eave_team_id = 8;\n  optional string eave_env = 9;\n  optional string opaque_eave_ctx = 10;\n  optional string eave_account = 11;\n  optional string eave_team = 12;\n}"
  name       = "eave_event"
  project    = var.project_id
  type       = "PROTOCOL_BUFFER"
  timeouts {
    create = null
    delete = null
  }
}

resource "google_pubsub_schema" "gpt_request_event_pubsub_schema" {
  definition = "syntax = \"proto3\";\n\nmessage GPTRequestEvent {\n  // reserve removed fields\n  reserved 12;\n  reserved \"file_identifier\";\n\n  optional string feature_name = 1;\n  string event_time = 2;\n  int64 duration_seconds = 3;\n  string eave_request_id = 4;\n  float input_cost_usd = 5;\n  float output_cost_usd = 6;\n  string input_prompt = 7;\n  string output_response = 8;\n  int64 input_token_count = 9;\n  int64 output_token_count = 10;\n  string model = 11;\n  optional string eave_team_id = 13;\n  optional string document_id = 14;\n}"
  name       = "gpt_request_event"
  project    = var.project_id
  type       = "PROTOCOL_BUFFER"
  timeouts {
    create = null
    delete = null
  }
}
