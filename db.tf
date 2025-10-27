# terraform {
#     required_providers {
#         google = {
#             source  = "hashicorp/google"
#             version = ">= 4.0"
#         }
#     }
#     required_version = ">= 1.0"
# }

# provider "google" {
#     project = var.project
#     region  = var.region
#     zone    = var.zone
# }

resource "google_compute_address" "pg_static_ip" {
  count = var.create_sample_db ? 1 : 0
  name   = "${var.prefix}-pg-static-ip"
  region = var.region
  depends_on = [ google_compute_network.vpc ]
}


resource "google_compute_instance" "postgres_vm" {
    count = var.create_sample_db ? 1 : 0
    name         = "${var.prefix}-postgres-vm"
    machine_type = "e2-medium"
    zone         = var.zone
    tags         = ["postgres-server"]

    boot_disk {
        initialize_params {
            image = "ubuntu-2204-lts"
            # image_project = "ubuntu-os-cloud"  # default for this image family
        }
    }

    network_interface {
        network    = google_compute_network.vpc.name
        subnetwork = google_compute_subnetwork.subnet.name

        # Assign static external IPs
        access_config {
            nat_ip = google_compute_address.pg_static_ip[0].address
        }
    }

    metadata_startup_script = <<-EOF
        #!/bin/bash
        set -e

        apt-get update -y
        apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

        apt-get update -y
        apt-get install -y docker-ce docker-ce-cli containerd.io

        systemctl enable docker
        systemctl start docker

        # Run postgres container
        /usr/bin/docker run -d \
            --name employee_postgres \
            -e POSTGRES_DB=employee_db \
            -e POSTGRES_USER=admin \
            -e POSTGRES_PASSWORD=admin \
            -p 5432:5432 \
            -v postgres_data:/var/lib/postgresql/data \
            postgres:15 || true

        EOF
}

resource "google_compute_firewall" "allow_postgres" {
    count = var.create_sample_db ? 1 : 0
    name    = "allow-postgres-5432"
    network = google_compute_network.vpc.name

    allow {
        protocol = "tcp"
        ports    = ["5432","22"]
    }
    source_ranges = ["0.0.0.0/0"]
}

output "postgres_vm_external_ip" {
    value = google_compute_instance.postgres_vm[0].network_interface[0].access_config[0].nat_ip
    description = "External IP of the VM running Postgres container"
}