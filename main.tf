# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Configuration
resource "google_compute_network" "vpc" {
  name                    = "${var.prefix}-vpc"
  auto_create_subnetworks = false
}

# Subnetwork Configuration
resource "google_compute_subnetwork" "subnet" {
  name          = "${var.prefix}-subnet"
  network       = google_compute_network.vpc.name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
}

resource "google_compute_firewall" "tcp_firewall" {
  name    = "${var.prefix}-tcp-firewall"
  network = google_compute_network.vpc.name
  allow {
    protocol = "tcp"
    ports    = var.tcp_ports
  }
  source_ranges = ["0.0.0.0/0"]
}

## Static External IPs for RDI Instances
resource "google_compute_address" "rdi_static_ips" {
  count  = var.rdi_HA ? 2 : 1 
  name   = "${var.prefix}-${count.index}-static-ip"
  region = var.region
}


# RDI Virtual Machine Instances
resource "google_compute_instance" "rdi_instances" {
  count        = var.rdi_HA ? 2 : 1 
  name         = "${var.prefix}-vm-${count.index}" 
  zone         = var.zone
  machine_type = var.machine_type 

  # Boot disk configuration
  boot_disk {
    initialize_params {
      image = var.image
      size  = var.disk_size 
      type  = var.disk_type     
    }
  }

  # Network Interfaces
  network_interface {
    network    = google_compute_network.vpc.name
    subnetwork = google_compute_subnetwork.subnet.name

    # Assign static external IPs
    access_config {
      nat_ip = google_compute_address.rdi_static_ips[count.index].address
    }
  }

  # Metadata for Startup Scripts
  metadata = {
    "startup-script" = templatefile(
        "${path.module}/rdi.sh",
        {
            rdi_db_index = var.rdi_db_index,
            rdi_db_host = var.rdi_db_host,
            rdi_db_port = var.rdi_db_port,
            rdi_db_username = var.rdi_db_username,
            rdi_db_password = var.rdi_db_password,
            rdi_version = var.rdi_version,
            external_ip = google_compute_address.rdi_static_ips[count.index].address
        }
    )
 }

  # Hostname Configuration
  hostname = "${var.prefix}-${count.index}-demo.redislabs.com"
}


output "RDI_vm_output" {
  value = {
    for idx, instance in google_compute_instance.rdi_instances:
    idx => {
      external_ip     = instance.network_interface[0].access_config[0].nat_ip
      vm_name         = "${var.prefix}-vm-${idx}"
    }
  } 
  description = "Details of RDI instances including internal IP, external IP, FQDN, machine type, and disk size."
}
