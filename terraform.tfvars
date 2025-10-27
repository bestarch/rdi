prefix = "abhi-rdi"
rdi_HA             = "false"

# Project Configuration
project_id         = "central-beach-194106"
region             = "asia-south1"
zone               = "asia-south1-a"

machine_type   = "n2-standard-4"
disk_size      = 80
disk_type          = "pd-balanced"
image              = "projects/rhel-cloud/global/images/rhel-9-v20250212"

tcp_ports          = ["22", "443"]


# RDI Database Configuration
rdi_db_index         = 4 # PostgreSQL
rdi_db_host         = "redis-15732.c48754.asia-south1-1.gcp.cloud.rlrcp.com"
rdi_db_port        = 15732
rdi_db_username    = "default"
rdi_db_password    = "admin"
rdi_version = "1.15.0"


# VPC and Subnet Configuration
subnet_cidr        = "10.0.1.0/24"

create_test_postgres_db = false
create_test_mysql_db = true