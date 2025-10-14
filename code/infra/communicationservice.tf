module "communication_service" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/communicationservice?ref=main"
  providers = {
    azurerm = azurerm
  }

  location                            = var.location
  resource_group_name                 = azurerm_resource_group.resource_group_container_app.name
  tags                                = var.tags
  communication_service_name          = "${local.prefix}-acs001"
  communication_service_data_location = var.communication_service_data_location
  diagnostics_configurations          = local.diagnostics_configurations
}
