resource "azurerm_private_endpoint" "private_endpoint" {
  name                = "${local.prefix}-search-tst-pe"
  resource_group_name = azurerm_resource_group.resource_group.name
  location            = var.location
  tags                = var.tags

  custom_network_interface_name = "${local.prefix}-search-tst-nic"
  private_service_connection {
    name                           = "${local.prefix}-search-tst-svc"
    is_manual_connection           = false
    private_connection_resource_id = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/fnf-test/providers/Microsoft.Search/searchServices/fnf-search"
    subresource_names              = ["searchService"]
  }
  subnet_id = azapi_resource.subnet_private_endpoints.id
  private_dns_zone_group {
    name = "${local.prefix}-search-tst-arecord"
    private_dns_zone_ids = [
      "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.search.windows.net"
    ]
  }

  lifecycle {
    ignore_changes = [
      #   private_dns_zone_group
    ]
  }
}
