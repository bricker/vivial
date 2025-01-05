output "request_header_modifier_standard" {
  value = {
    type = "RequestHeaderModifier"
    requestHeaderModifier = {
      set = [
        {
          name  = "eave-lb"
          value = "1"
        },
        {
          name  = "eave-lb-geo-region"
          value = "{client_region}"
        },
        {
          name  = "eave-lb-geo-subdivision"
          value = "{client_region_subdivision}"
        },
        {
          name  = "eave-lb-geo-city"
          value = "{client_city}"
        },
        {
          name  = "eave-lb-geo-coordinates"
          value = "{client_city_lat_long}"
        },
        {
          name  = "eave-lb-client-ip"
          value = "{client_ip_address}"
        },
      ]
    }
  }
}

output "response_header_modifier_standard" {
  value = {
    type = "ResponseHeaderModifier"
    responseHeaderModifier = {
      set = [
        {
          name  = "server"
          value = "n/a"
        }
      ]
    }
  }
}
