locals {
  app_service_accounts = {
    eave_core = {
      account_id   = "sa-eave-core",
      display_name = "Eave Core App",
    }
    eave_www = {
      account_id   = "sa-eave-www",
      display_name = "Eave Website",
    }
    eave_slack = {
      account_id   = "sa-eave-slack",
      display_name = "Eave Slack App",
    }
    eave_github = {
      account_id   = "sa-eave-github",
      display_name = "Eave Github App",
    }
    eave_confluence = {
      account_id   = "sa-eave-confluence",
      display_name = "Eave Confluence App",
    }
    eave_confluence = {
      account_id   = "sa-eave-jira",
      display_name = "Eave Jira App",
    }
  }
}

resource "google_service_account" "app_service_accounts" {
  for_each = local.app_service_accounts

  account_id   = each.value.account_id
  display_name = each.value.display_name
  disabled     = false
  timeouts {
    create = null
  }
}
