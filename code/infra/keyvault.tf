module "key_vault" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/keyvault?ref=main"
  providers = {
    azurerm = azurerm
    time    = time
  }

  location                             = var.location
  resource_group_name                  = azurerm_resource_group.resource_group.name
  tags                                 = var.tags
  key_vault_name                       = "${local.prefix}-kv001"
  key_vault_sku_name                   = "standard"
  key_vault_soft_delete_retention_days = 7
  diagnostics_configurations           = local.diagnostics_configurations
  subnet_id                            = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds        = var.connectivity_delay_in_seconds
  private_dns_zone_id_vault            = var.private_dns_zone_id_vault
}

resource "azurerm_key_vault_secret" "key_vault_secret_communication_service_primary_connection_string" {
  key_vault_id = module.key_vault.key_vault_id

  name         = "acs-connection-string"
  content_type = "text/plain"
  value        = module.communication_service.communication_service_primary_connection_string
}

resource "azurerm_key_vault_secret" "key_vault_secret_application_insights_connection_string" {
  key_vault_id = module.key_vault.key_vault_id

  name         = "ai-connection-string"
  content_type = "text/plain"
  value        = module.application_insights.application_insights_connection_string
}

resource "azurerm_key_vault_secret" "key_vault_secret_aoai_primary_access_key" {
  key_vault_id = module.key_vault.key_vault_id

  name         = "aoai-primary-access-key"
  content_type = "text/plain"
  value        = module.ai_service.cognitive_account_primary_access_key
}
