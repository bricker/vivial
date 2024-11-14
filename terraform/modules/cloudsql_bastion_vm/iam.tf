resource "google_compute_instance_iam_binding" "bastion_vm_compute_oslogin_role_members" {
  # Grant developers access to login to the bastion VM through IAP
  instance_name = google_compute_instance.bastion.name
  role          = data.google_iam_role.compute_oslogin_role.id
  members       = var.accessors
}

resource "google_service_account_iam_binding" "bastion_sa_service_account_user_role_members" {
  # Give developers access to use the service account installed on the bastion VM
  service_account_id = google_service_account.bastion_sa.id
  role               = data.google_iam_role.service_account_user_role.id
  members            = var.accessors
}