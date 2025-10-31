module "ai_service" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/aiservice?ref=main"
  providers = {
    azurerm = azurerm
    azapi   = azapi
    time    = time
  }

  location                                                = var.location_aoai
  location_private_endpoint                               = var.location
  resource_group_name                                     = azurerm_resource_group.resource_group.name
  tags                                                    = var.tags
  cognitive_account_name                                  = "${local.prefix}-ai001"
  cognitive_account_kind                                  = "OpenAI"
  cognitive_account_sku                                   = "S0"
  cognitive_account_firewall_bypass_azure_services        = false
  cognitive_account_outbound_network_access_restricted    = true
  cognitive_account_outbound_network_access_allowed_fqdns = []
  cognitive_account_local_auth_enabled                    = false
  cognitive_account_deployments                           = {}
  diagnostics_configurations                              = local.diagnostics_configurations
  subnet_id                                               = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds                           = var.connectivity_delay_in_seconds
  private_dns_zone_id_cognitive_account                   = var.private_dns_zone_id_open_ai
  customer_managed_key                                    = var.customer_managed_key
}
