resource "google_compute_address" "mysql_static_ip" {
  count = var.create_test_mysql_db ? 1 : 0
  name   = "${var.prefix}-mysql-static-ip-${random_string.suffix.result}"
  region = var.region
  depends_on = [ google_compute_network.vpc ]
}

resource "google_compute_instance" "mysql_vm" {
    count = var.create_test_mysql_db ? 1 : 0
    name         = "${var.prefix}-mysql-vm-${random_string.suffix.result}"
    machine_type = "e2-medium"
    zone         = var.zone
    tags         = ["mysql-server"]

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
            nat_ip = google_compute_address.mysql_static_ip[0].address
        }
    }

    metadata_startup_script = <<-EOF
        #!/bin/bash
        set -e

        log_file="/test_db_mysql.log"
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

        # Run mysql container
        /usr/bin/docker run -d \
            --name mysql_ecom_db \
            -e MYSQL_ROOT_PASSWORD=admin \
            -e MYSQL_DATABASE=sample_shop \
            -p 3306:3306 \
            -v mysql_data:/var/lib/mysql \
            mysql:8.0 || true

        echo "MySQL container started successfully" >> $${log_file}

        # Install python, pip and git
        apt-get install -y python3 python3-pip git

        # Install Python DB dependency for mysql script
        pip3 install --upgrade pip
        pip3 install mysql-connector-python

        # Clone the repo (or update if exists)
        mkdir -p /opt
        if [ ! -d /opt/rdi ]; then
            git clone --depth=1 https://github.com/bestarch/rdi.git /opt/rdi || {
                echo "git clone failed for https://github.com/bestarch/rdi.git" >> $${log_file}
            }
        else
            git -C /opt/rdi pull --ff-only || {
                echo "git pull failed for /opt/rdi (will continue)" >> $${log_file}
            }
        fi

        echo "Repo https://github.com/bestarch/rdi.git cloned at location /opt/rdi" >> $${log_file}

        # Change to sample_db_mysql folder
        cd /opt/rdi/sample_db_mysql || exit 0
        pip3 install -r requirements.txt || true

        # Export MySQL connection env vars (matches container run above)
        export MYSQL_HOST=127.0.0.1
        export MYSQL_PORT=3306
        export MYSQL_USER=root
        export MYSQL_PASSWORD=admin

        echo "Attempting to run ecom_db.py" >> $${log_file}

        # Retry running the Python script until it succeeds (or until attempts exhausted)
        attempts=0
        max_attempts=5
        until python3 ecom_db.py; do
            attempts=$((attempts+1))
            if [ "$${attempts}" -ge "$${max_attempts}" ]; then
                echo "ecom_db.py failed after $${attempts} attempts" >&2
                echo "Could not run ecom_db.py in $${attempts} attempts" >> $${log_file}
                break
            fi
            echo "ecom_db.py failed, retrying in 5s ($${attempts}/$${max_attempts})"
            sleep 5
        done
        if [ "$${attempts}" -le "$${max_attempts}" ]; then
            echo "ecom_db.py executed successfully in $${attempts} attempts" >> $${log_file}
        fi

        EOF
}

resource "google_compute_firewall" "allow_mysql" {
    count = var.create_test_mysql_db ? 1 : 0
    name    = "allow-mysql-3306"
    network = google_compute_network.vpc.name

    allow {
        protocol = "tcp"
        ports    = ["3306","22"]
    }
    source_ranges = ["0.0.0.0/0"]
}

output "mysql_vm_external_ip" {
    value = var.create_test_mysql_db ? google_compute_instance.mysql_vm[0].network_interface[0].access_config[0].nat_ip : null
    description = "External IP of the VM running MySQL container"
}
