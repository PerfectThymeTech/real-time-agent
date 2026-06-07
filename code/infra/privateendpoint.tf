resource "azurerm_private_endpoint" "private_endpoint" {
  name                = "${local.prefix}-oai-tst-pe"
  resource_group_name = azurerm_resource_group.resource_group.name
  location            = var.location
  tags                = var.tags

  custom_network_interface_name = "${local.prefix}-oai-tst-nic"
  private_service_connection {
    name                           = "${local.prefix}-oai-tst-svc"
    is_manual_connection           = true
    private_connection_resource_id = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/aml-test-rg/providers/Microsoft.CognitiveServices/accounts/aoai-mabuss-cs001"
    request_message                = "Private Endpoint Connection Request from Data Landing Zone Stamp Application with prefix: ${local.prefix}"
    subresource_names              = ["account"]
  }
  subnet_id = azapi_resource.subnet_private_endpoints.id
  private_dns_zone_group {
    name = "${local.prefix}-oai-tst-arecord"
    private_dns_zone_ids = [
      var.private_dns_zone_id_open_ai
    ]
  }

  lifecycle {
    ignore_changes = [
      #   private_dns_zone_group
    ]
  }
}
