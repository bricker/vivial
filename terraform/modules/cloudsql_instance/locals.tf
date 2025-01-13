locals {
  preset_production = data.google_project.default.name == "eave-production"
}
