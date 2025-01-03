module "dns_zone_base_domain" {
  source     = "../../modules/dns_zone"
  dns_domain = local.dns_domain

  records = [
    {
      type = "TXT"
      datas = [
        "google-site-verification=fW2nsEe34FlVdFO2V0fqZjvw5uaid6Wf7yTG2hiUOz0",
        "\"v=spf1 include:mailgun.org ~all\"", # Squarespace Email Forwarding
      ]
    },

    # Squarespace Email Forwarding
    {
      type      = "TXT"
      subdomain = "k1._domainkey"
      datas     = ["\"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC/xFlJj6NXboJNUahgnsiGzyXmVjaSdq8Dnql+oYc8FWi/JSoi6ZekhS4hv9IRduG2klvPHc34gqQwjkWWD9aQLGG/QOEvVUACSa4NKIF5SnPG4sUbxjYH0ffB8OpTkugogZsGdStmVgeg54cPr7KVtM4SrZRqu1XB/4G0WZTBHwIDAQAB\""]
    },

    # Squarespace Email Forwarding
    {
      type = "MX"
      datas = [
        "10 mxa.mailgun.org.",
        "10 mxb.mailgun.org.",
      ]
    },
  ]
}

module "dns_zone_run" {
  source     = "../../modules/dns_zone"
  dns_domain = "eave.run"

  records = [
    {
      type      = "A"
      subdomain = "*"
      datas     = ["127.0.0.1"] # It is important that this is an IPv4 address, because our local development setup only guarantees IPv4 binding
    },

    {
      type = "TXT"
      datas = [
        "\"v=spf1 include:mailgun.org ~all\"" # Squarespace Email Forwarding
      ]
    },

    # Squarespace Email Forwarding
    {
      type      = "TXT"
      subdomain = "smtp._domainkey"
      datas     = ["\"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDSH/qwtc9PfZE5ukWs0DGdHrud0enSN3WQ5EQGaiAA42fEz64A+0UWvEFqhPVV87VJrUr7LZ7KZugguKHAhSuX5m21SxJvo6LPTSN2j40XApCJpBnce+u/pgcZyEAgfh+zD+Kd9ODL+PLoYxH0saJfZoSI0kjX2xeq6Kolqf1xawIDAQAB\""]
    },

    # Squarespace Email Forwarding
    {
      type = "MX"
      datas = [
        "10 mxa.mailgun.org.",
        "10 mxb.mailgun.org.",
      ]
    },

  ]
}

module "dns_zone_pink" {
  source      = "../../modules/dns_zone"
  dns_domain = "eave.pink"
  records = [
    {
      type      = "A"
      subdomain = "*"
      datas     = ["127.0.0.1"] # It is important that this is an IPv4 address, because our local development setup only guarantees IPv4 binding
    },
  ]
}

module "dns_zone_red" {
  source      = "../../modules/dns_zone"
  dns_domain = "eave.red"
  records = [
    {
      type      = "A"
      subdomain = "*"
      datas     = ["127.0.0.1"] # It is important that this is an IPv4 address, because our local development setup only guarantees IPv4 binding
    },
  ]
}

module "dns_zone_blue" {
  source      = "../../modules/dns_zone"
  dns_domain = "eave.blue"
  records = [
    {
      type      = "A"
      subdomain = "*"
      datas     = ["127.0.0.1"] # It is important that this is an IPv4 address, because our local development setup only guarantees IPv4 binding
    },
  ]
}