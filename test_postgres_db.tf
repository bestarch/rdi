
resource "google_compute_address" "pg_static_ip" {
  count = var.create_test_postgres_db ? 1 : 0
  name   = "${var.prefix}-pg-static-ip"
  region = var.region
  depends_on = [ google_compute_network.vpc ]
}

resource "google_compute_instance" "postgres_vm" {
    count = var.create_test_postgres_db ? 1 : 0
    name         = "${var.prefix}-postgres-vm"
    machine_type = "e2-medium"
    zone         = var.zone
    tags         = ["postgres-server"]

    boot_disk {
        initialize_params {
            image = "ubuntu-2204-lts"
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

        log_file="/test_db_postgres.log"
        echo "Installing docker runtime" >> $${log_file}
        apt-get update -y
        apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

        apt-get update -y
        apt-get install -y docker-ce docker-ce-cli containerd.io

        systemctl enable docker
        systemctl start docker
        echo "Docker runtime installed successfully" >> $${log_file}

        # Run postgres container
        /usr/bin/docker run -d \
            --name employee_postgres \
            -e POSTGRES_DB=employee_db \
            -e POSTGRES_USER=admin \
            -e POSTGRES_PASSWORD=admin \
            -p 5432:5432 \
            -v postgres_data:/var/lib/postgresql/data \
            postgres:15 || true

        echo "Postgres container started successfully" >> $${log_file}

        # Install python, pip and git
        apt-get install -y python3 python3-pip git

        # Install Python DB dependency
        pip3 install --upgrade pip
        pip3 install psycopg2-binary

        # Clone the repo (or update if exists)
        if [ ! -d /opt/rdi ]; then
            git clone https://github.com/bestarch/rdi.git /opt/rdi
        else
            cd /opt/rdi && git pull || true
        fi

        echo "Repo https://github.com/bestarch/rdi.git cloned at location /opt/rdi" >> $${log_file}

        # Change to sample_db folder
        cd /opt/rdi/sample_db || exit 0  
        pip3 install -r requirements.txt

        # Export Postgres connection env vars (matches container run above)
        export POSTGRES_DB=127.0.0.1
        export POSTGRES_PORT=5432
        export POSTGRES_USER=admin
        export POSTGRES_PASSWORD=admin

        echo "Attempting to run employee_db.py" >> $${log_file}

        # Retry running the Python script until it succeeds (or until attempts exhausted)
        attempts=0
        max_attempts=3
        until python3 employee_db.py; do
            attempts=$((attempts+1))
            if [ "$attempts" -ge "$max_attempts" ]; then
                echo "employee_db.py failed after $attempts attempts" >&2
                echo "Could not run employee_db.py in $attempts attempts" >> $${log_file}
                break
            fi
            echo "employee_db.py failed, retrying in 5s ($attempts/$max_attempts)"
            sleep 5
        done
        if [ "$attempts" -le "$max_attempts" ]; then
            echo "employee_db.py executed successfully in $attempts attempts" >> $${log_file}
        fi

        echo "Setting wal_level to 'logical' via ALTER SYSTEM" >> $${log_file}

        if /usr/bin/docker exec employee_postgres psql -U admin -d employee_db -c "ALTER SYSTEM SET wal_level = 'logical';" >> $${log_file} 2>&1; then
            echo "Reloading Postgres configuration" >> $${log_file}
            /usr/bin/docker restart employee_postgres
            /usr/bin/docker exec employee_postgres psql -U admin -d employee_db -tAc "SHOW wal_level;"  >> $${log_file} 
        else
            echo "Failed to set wal_level" >> $${log_file}
        fi

        EOF
}

resource "google_compute_firewall" "allow_postgres" {
    count = var.create_test_postgres_db ? 1 : 0
    name    = "allow-postgres-5432"
    network = google_compute_network.vpc.name

    allow {
        protocol = "tcp"
        ports    = ["5432","22"]
    }
    source_ranges = ["0.0.0.0/0"]
}

output "postgres_vm_external_ip" {
    value = var.create_test_postgres_db ? google_compute_instance.postgres_vm[0].network_interface[0].access_config[0].nat_ip : null
    description = "External IP of the VM running Postgres container"
}