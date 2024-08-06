locals {
  uptime_checks_map = { for uptime_check in var.uptime_checks : uptime_check.service => uptime_check }
}