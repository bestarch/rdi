#!/bin/bash

log_file="/rdi_installation.log"

# Function to log debugging variables
log_info() {
  echo "RDI rdi_db_index: ${rdi_db_index}" >> $${log_file}
  echo "RDI DB Host: ${rdi_db_host}" >> $${log_file}
  echo "RDI DB Port: ${rdi_db_port}" >> $${log_file}
  echo "RDI DB Username: ${rdi_db_username}" >> $${log_file}
  echo "RDI DB Password: ${rdi_db_password}" >> $${log_file}
  echo "RDI version: ${rdi_version}" >> $${log_file}
  echo "IP: ${external_ip}" >> $${log_file}
}


download_rdi_package() {
  echo "Installing Redis CLI and download RDI package..." >> $${log_file} && \
  sudo yum install -y wget dnsutils net-tools redis && \
  sudo wget -O "/opt/rdi-installation-${rdi_version}.tar.gz" "https://qa-onprem.s3.amazonaws.com/redis-di/${rdi_version}/rdi-installation-${rdi_version}.tar.gz" && \
  
  echo "Successfully downloaded RDI package" >> $${log_file} && \
  sudo tar -xvf "/opt/rdi-installation-${rdi_version}.tar.gz" -C /opt && \
  cd "/opt/rdi_install/${rdi_version}" || { log "Directory not found: /opt/rdi_install/${rdi_version}"; exit 1; } && \
  check_tool redis-cli
}


create_rdi_config_file() {
  config_file_path="/opt/silent.toml"
  echo "Creating RDI configuration file at '$${config_file_path}'..." >> $${log_file}

  # Write the TOML file
  cat <<EOL > "$${config_file_path}"
title = "RDI Silent Installer Config"

scaffold = true
# Integer to specify the source database type for scaffolding. The options are 2 (MySQL/MariaDB), 3 (Oracle), 4 (PostgreSQL), and 5 (SQL Server)
db_index = ${rdi_db_index}
deploy_directory = "/opt/rdi/config"

# Needed if the installer detects a DNS resolver with a loopback address
# as an upstream DNS server
nameservers = ["8.8.8.8", "8.8.4.4"]

[rdi.database]
host = "${rdi_db_host}"
port = ${rdi_db_port}
username = "${rdi_db_username}"
password = "${rdi_db_password}"
use_existing_rdi = true
ssl = false

# Uncomment the properties in this section only if the RDI
# database uses TLS/mTLS.

# [rdi.database.certificates]
# ca = "/home/ubuntu/rdi/certs/ca.crt"
# cert = "/home/ubuntu/rdi/certs/client.crt"
# key = "/home/ubuntu/rdi/certs/client.key"
# passphrase = "foobar"
EOL

  echo "RDI configuration file created successfully at '$${config_file_path}'." >> $${log_file}
}


# Function to install RDI
install_rdi() {
  echo "Installing RDI..." >> $${log_file} && \
  cd /opt/rdi_install/${rdi_version} && \
  sudo ./install.sh --file /opt/silent.toml && \
  echo "Installed RDI" >> $${log_file} && \
#   if [ "$(printf '%s\n' "${rdi_version}" "1.15.999" | sort -V | head -n1)" = "${rdi_version}" ]; then
#     sudo ./install.sh --file /opt/silent.toml || {
#         echo "ERROR: RDI installer failed" >> $${log_file}
#         return 1
#     }
#   else
#     echo "RDI ${rdi_version} no longer supports silent installation; please complete the installation following the latest RDI documentation." >> $${log_file}
#   fi
  rm -rf "/opt/rdi-installation-${rdi_version}.tar.gz" && \
  check_tool redis-di
}



check_tool() {
  if command -v $1 >/dev/null 2>&1; then
      tool_version=$($1 --version 2>&1)
      echo "$1 is installed: $tool_version" >> $${log_file}
  else
      echo "$1 installation failed." >> $${log_file}
  fi
}

# Main function
main() {
  log_info
  download_rdi_package
  create_rdi_config_file
  install_rdi
}

# Execute the main function
main