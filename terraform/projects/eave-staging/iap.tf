import {
  id = "projects/264481035543/brands/264481035543"
  to = module.iap.google_iap_brand.project
}

import {
  id = "projects/264481035543/brands/264481035543/identityAwareProxyClients/264481035543-ebotr22qbro4jbre1otq2njkacdcrb21.apps.googleusercontent.com"
  to = module.iap.google_iap_client.default
}

module "iap" {
  source = "../../modules/iap"
  dns_domain = local.dns_domain
  application_title = "Eave (Staging)"
  gateways = data.google_compute_backend_service.gateways
}
