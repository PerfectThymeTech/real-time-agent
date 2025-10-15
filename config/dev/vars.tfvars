# General variables
location    = "northeurope"
environment = "dev"
prefix      = "voi-aig"
tags = {
  "workload" = "voice-agent"
}

# Service variables
container_image_reference           = "todo"
communication_service_data_location = "Europe"

# HA/DR variables
zone_redundancy_enabled = false

# Logging and monitoring variables
log_analytics_workspace_id = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-logging-rg/providers/Microsoft.OperationalInsights/workspaces/ptt-dev-log001"

# Identity variables
service_principal_name_terraform_plan = ""

# Network variables
vnet_id                       = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-hub-northeurope-rg/providers/Microsoft.Network/virtualNetworks/ptt-dev-vnet001"
nsg_id                        = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-hub-northeurope-rg/providers/Microsoft.Network/networkSecurityGroups/ptt-dev-default-nsg001"
route_table_id                = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-hub-northeurope-rg/providers/Microsoft.Network/routeTables/ptt-dev-default-rt001"
subnet_cidr_container_app     = "10.0.2.64/26"
subnet_cidr_private_endpoints = "10.0.2.128/26"

# DNS variables
private_dns_zone_id_vault = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.vaultcore.azure.net"

# Customer-managed key variables
customer_managed_key = null
