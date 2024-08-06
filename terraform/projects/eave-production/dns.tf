# Hello.
# The DNS nameservers for eave.fyi are hosted by Squarespace.
# This DNS zone and all included records mirror the records in Squarespace.
# Why don't I just switch nameservers?
# Fear. Mostly that our email and google workspace services will stop working.
# So, any time a record is added or modified by Terraform,
# you need to go into the Squarespace DNS portal and make the change there manually.

module "dns_zone_base_domain" {
  source      = "../../modules/dns_zone"
  root_domain = local.root_domain

  records = [
    ## Google Workspace
    {
      type = "MX"
      datas = [
        "1 aspmx.l.google.com.",
        "5 alt1.aspmx.l.google.com.",
        "5 alt2.aspmx.l.google.com.",
        "10 alt3.aspmx.l.google.com.",
        "10 alt4.aspmx.l.google.com.",
      ]
    },

    ## Custom Records
    {
      type = "A",
      datas = [
        "198.185.159.144",
        "198.185.159.145",
        "198.49.23.144",
        "198.49.23.145",
      ],
    },
    {
      type = "TXT",
      datas = [
        "\"v=spf1 include:_spf.google.com ~all\"",
        "slack-domain-verification=1SCpHl5o3Nujmr3pdBCFAP3lIKwr81hSUQD9FJ5y",
      ],
    },
    {
      type      = "TXT",
      subdomain = "_dmarc"
      datas = [
        "\"v=DMARC1;p=none;rua=mailto:dmarc-reports@eave.fyi;ruf=mailto:dmarc-reports@eave.fyi;sp=none;ri=86400\"",
      ],
    },
    {
      type      = "TXT",
      subdomain = "google._domainkey"
      datas = [
        # Note that this string is specially formatted for the TXT record, with quotes injected every 255 characters.
        "\"v=DKIM1;k=rsa;p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAg5ylMKypT874J8l+7Eh2BrWLLI1tRKTkXmUGgMv673x6UJypEulq6Q+QfS2EmqT4t7bLCC9aEIDRpAapKm6YmX4wZyyv45GEuFgJgLkSSrQ7vJKl6i6Nz6rkykK14GovOBPTvLOwm0hy8C0l7KuCj/VGfG3uRT8ge0yu/qiGNApQKLCJdcPuS2o3bmxqgqfzi\" \"6X8rEvWOlqM7mscv/z/xXqTiwMlwdk6jAB1bDSVCmc76mYACDfTQ1XoflDG0E9H3oIa1I6PMryE3hgQpBxF9kL2gSD7XIqWNn+zK6NEPgyeBXf5RKylW81BT8FWKjitQZI4GTBUJueYYDmPFdoDDwIDAQAB\"",
      ],
    },
    {
      type      = "CNAME",
      subdomain = "tlhahrxjw5anplz9yyg7"
      datas = [
        "verify.squarespace.com.",
      ],
    },
    {
      type      = "CNAME",
      subdomain = "www"
      datas = [
        "ext-cust.squarespace.com.",
      ],
    },

    ## Google Records
    {
      type      = "CNAME",
      subdomain = "ala55kg6in7z"
      datas = [
        "gv-boykc4q5i3uucd.dv.googlehosted.com.",
      ],
    },
    {
      type      = "CNAME",
      subdomain = "jjeu6awts77f"
      datas = [
        "gv-4y2ruslvifcdd7.dv.googlehosted.com.",
      ],
    },
    {
      type      = "CNAME",
      subdomain = "orgaarcdmnxh"
      datas = [
        "gv-cdd2zw5qt2mqji.dv.googlehosted.com.",
      ],
    },
  ]
}
