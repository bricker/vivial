module "dns_zone_base_domain" {
  source      = "../../modules/dns_zone"
  root_domain = local.root_domain

  records = [ {
    type = "TXT"
    datas = ["google-site-verification=fW2nsEe34FlVdFO2V0fqZjvw5uaid6Wf7yTG2hiUOz0"]
  } ]
}

module "dns_zone_pink" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.pink"
}

module "dns_zone_red" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.red"
}

module "dns_zone_blue" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.blue"
}

module "dns_zone_run" {
  source      = "../../modules/dns_zone"
  root_domain = "eave.run"

  records = [ {
    type = "CNAME"
    subdomain="*"
    datas = [ "localhost." ]
  } ]
}
