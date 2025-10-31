resource "azurerm_container_app_environment" "container_app_environment" {
  name                = "${local.prefix}-cae001"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
  tags                = var.tags

  dapr_application_insights_connection_string = module.application_insights.application_insights_connection_string
  infrastructure_resource_group_name          = "${local.prefix}-cae001-rg"
  infrastructure_subnet_id                    = azapi_resource.subnet_container_app.id
  internal_load_balancer_enabled              = true
  logs_destination                            = "azure-monitor"
  mutual_tls_enabled                          = false
  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
  }
  # workload_profile {
  #   name                  = "D4"
  #   workload_profile_type = "D4"
  #   minimum_count         = 1
  #   maximum_count         = 3
  # }
  zone_redundancy_enabled = var.zone_redundancy_enabled
}

resource "azurerm_monitor_diagnostic_setting" "diagnostic_setting_container_app_environment" {
  for_each = { for index, value in local.diagnostics_configurations :
    index => {
      log_analytics_workspace_id = value.log_analytics_workspace_id,
      storage_account_id         = value.storage_account_id
    }
  }
  name                       = "applicationLogs-${each.key}"
  target_resource_id         = azurerm_container_app_environment.container_app_environment.id
  log_analytics_workspace_id = each.value.log_analytics_workspace_id == "" ? null : each.value.log_analytics_workspace_id
  storage_account_id         = each.value.storage_account_id == "" ? null : each.value.storage_account_id

  dynamic "enabled_log" {
    iterator = entry
    for_each = data.azurerm_monitor_diagnostic_categories.diagnostic_categories_container_app_environment.log_category_groups
    content {
      category_group = entry.value
    }
  }

  dynamic "metric" {
    iterator = entry
    for_each = data.azurerm_monitor_diagnostic_categories.diagnostic_categories_container_app_environment.metrics
    content {
      category = entry.value
      enabled  = true
    }
  }
}
