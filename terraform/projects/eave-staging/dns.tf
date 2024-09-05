module "dns_zone_base_domain" {
  source      = "../../modules/dns_zone"
  root_domain = local.root_domain

  records = [
    {
      type  = "TXT"
      datas = ["google-site-verification=fW2nsEe34FlVdFO2V0fqZjvw5uaid6Wf7yTG2hiUOz0"]
    },

    # Squarespace Email Forwarding records
    {
      type = "MX"
      datas = [
        "10 mxa.mailgun.org.",
        "10 mxb.mailgun.org.",
      ]
    },
    {
      type  = "TXT"
      datas = ["\"v=spf1 include:mailgun.org ~all\""]
    },
    {
      type      = "TXT"
      subdomain = "k1._domainkey"
      datas     = ["\"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC/xFlJj6NXboJNUahgnsiGzyXmVjaSdq8Dnql+oYc8FWi/JSoi6ZekhS4hv9IRduG2klvPHc34gqQwjkWWD9aQLGG/QOEvVUACSa4NKIF5SnPG4sUbxjYH0ffB8OpTkugogZsGdStmVgeg54cPr7KVtM4SrZRqu1XB/4G0WZTBHwIDAQAB\""]
    },
    # End Squarespace Email Forwarding records
  ]
}

module "dns_zone_pink" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.pink"
  records = [
    # Squarespace Email Forwarding records
    {
      type = "MX"
      datas = [
        "10 mxa.mailgun.org.",
        "10 mxb.mailgun.org.",
      ]
    },
    {
      type  = "TXT"
      datas = ["\"v=spf1 include:mailgun.org ~all\""]
    },
    {
      type      = "TXT"
      subdomain = "smtp._domainkey"
      datas     = ["\"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+0qX3T1/M8rQqjTdgO8YttFlTBxy11zwOcG1+u85J4CqvbzYvFlwd2C7yKIUrIMbsrZ2LEtfDxoFJxCAKVq30Dp7ggxMarIy4tT87JAWUo5TkjRR2SKiE0KJs30MnHWd+Ua/iRvTVXnA3z/w1EC3AM0r8t8gd0uMcRw6ND5UsLwIDAQAB\""]
    },
    # End Squarespace Email Forwarding records
  ]
}

module "dns_zone_red" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.red"
  records = [
    # Squarespace Email Forwarding records
    {
      type = "MX"
      datas = [
        "10 mxa.mailgun.org.",
        "10 mxb.mailgun.org.",
      ]
    },
    {
      type  = "TXT"
      datas = ["\"v=spf1 include:mailgun.org ~all\""]
    },
    {
      type      = "TXT"
      subdomain = "mailo._domainkey"
      datas     = ["\"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbz2AWr9je3pA+L+aCRfVhu4jJoQstZpP/2AB42gmHd3TjjrpK4J2xHmTfEA+FyBlbhMxegVvlWErCVf9JSb9sjKYca/HAjKqGbCuJ2weFzuB55q+8kv5S3P0mvbg09wiY7UsrPD3Tt+vqWm5P25PXY5cBakNQ6Uabfmykq6kFYwIDAQAB\""]
    },
    # End Squarespace Email Forwarding records
  ]
}

module "dns_zone_blue" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.blue"
  records = [
    # Squarespace Email Forwarding records
    {
      type = "MX"
      datas = [
        "10 mxa.mailgun.org.",
        "10 mxb.mailgun.org.",
      ]
    },
    {
      type  = "TXT"
      datas = ["\"v=spf1 include:mailgun.org ~all\""]
    },
    {
      type      = "TXT"
      subdomain = "k1._domainkey"
      datas     = ["\"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDB+NSDNt0f2J3r8blL9UpxVBfPqROtbTIrNO2ZEdph6J9MxzBB1B2bG05zAhAtJ03OvZo8UANkBWf2heCjSR2tVhEeaphHOdFzx07gHmf1qdxDpJvm+vcRVP9xSOEViVs0anEFLX7sTMyuQ4PBXVqPglrKXaLCfqSk4e90mPGQ2QIDAQAB\""]
    },
    # End Squarespace Email Forwarding records
  ]
}

module "dns_zone_run" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.run"

  records = [
    {
      type      = "A"
      subdomain = "*"
      datas     = ["127.0.0.1"] # It is important that this is an IPv4 address, because our local development setup only guarantees IPv4 binding
    },

    # Squarespace Email Forwarding records
    {
      type = "MX"
      datas = [
        "10 mxa.mailgun.org.",
        "10 mxb.mailgun.org.",
      ]
    },
    {
      type  = "TXT"
      datas = ["\"v=spf1 include:mailgun.org ~all\""]
    },
    {
      type      = "TXT"
      subdomain = "smtp._domainkey"
      datas     = ["\"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDSH/qwtc9PfZE5ukWs0DGdHrud0enSN3WQ5EQGaiAA42fEz64A+0UWvEFqhPVV87VJrUr7LZ7KZugguKHAhSuX5m21SxJvo6LPTSN2j40XApCJpBnce+u/pgcZyEAgfh+zD+Kd9ODL+PLoYxH0saJfZoSI0kjX2xeq6Kolqf1xawIDAQAB\""]
    },
    # End Squarespace Email Forwarding records
  ]
}
