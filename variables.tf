variable "prefix" {
  type = string
  description = "prefix for the resources"
  default = "abhi-rdi"
}
variable "project_id" {
  description = "Google Cloud Project ID"
}

variable "region" {
  description = "Region for resources"
  default             = "asia-south1"
}

variable "zone" {
  description = "Zone for the VMs"
  default     = "asia-south1-a"
}

variable "rdi_db_host" {
  description = "RDI BDB Host"
    type        = string
}

variable "rdi_db_port" {
  description = "RDI DB port"
  type        = number
}
variable "rdi_db_username" {
  description = "RDI DB username"
    type        = string
}

variable "rdi_db_password" {
  description = "RDI DB password"
  type        = string
}

variable "subnet_cidr" {
  description = "CIDR range for the subnet"
}

variable "image" {
  description = "The image to use for the VM instances"
  type        = string
  default     = "projects/rhel-cloud/global/images/rhel-9-v20250212"
}

variable "rdi_HA" {
  description = "Determine HA for RDI"
  type        = bool
  default     = false
}

variable "rdi_version" {
  description = "Version of Redis Data Integration (RDI)"
  type        = string
  default     = "1.15.0"
}

variable "rdi_db_index" {
  description = "Index for RDI DB"
  type        = number
}

variable "instance_count" {
  description = "Number of VM instances to create"
  type        = number
  default     = 1

  validation {
    condition     = var.instance_count % 2 == 1 && var.instance_count >= 1
    error_message = "The instance_count must be an odd number. Redis clusters require an odd number for quorum."
  }
}

variable "disk_size" {
  description = "size of boot disk"
  default     = 20
}

variable "machine_type" {
  description = "machine type to use"
  default     = "n4-standard-2"
}

variable "disk_type" {
  description = "Disk type for boot disk"
  default     = "pd-standard"
}

variable "tcp_ports" {
  description = "List of TCP ports to open in the firewall"
  type        = list(string)
  default     = ["22", "80", "443"]
}

variable "firewall_tcp_name" {
  description = "Name of the TCP firewall rule"
  type        = string
  default     = "rdi-tcp-firewall"
}

variable "create_test_postgres_db" {
  description = "Whether to create a sample Postgres database instance"
  type        = bool
  default     = true
}

variable "create_test_mysql_db" {
  description = "Whether to create a sample MySQL database instance"
  type        = bool
  default     = true
}
