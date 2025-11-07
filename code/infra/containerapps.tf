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

resource "azurerm_container_app" "container_app_backend" {
  name                = "${local.prefix}-ca001-backend"
  resource_group_name = azurerm_resource_group.resource_group.name
  tags                = var.tags
  identity {
    type = "UserAssigned"
    identity_ids = [
      module.user_assigned_identity.user_assigned_identity_id
    ]
  }

  container_app_environment_id = azurerm_container_app_environment.container_app_environment.id
  ingress {
    allow_insecure_connections = false
    client_certificate_mode    = "accept"
    external_enabled           = true
    # ip_security_restriction {

    # }
    target_port = 80
    transport   = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }
  # max_inactive_revisions =
  revision_mode = "Single"
  secret {
    name                = "acs-connection-string"
    identity            = module.user_assigned_identity.user_assigned_identity_id
    key_vault_secret_id = azurerm_key_vault_secret.key_vault_secret_communication_service_primary_connection_string.id
  }
  secret {
    name                = "ai-connection-string"
    identity            = module.user_assigned_identity.user_assigned_identity_id
    key_vault_secret_id = azurerm_key_vault_secret.key_vault_secret_application_insights_connection_string.id
  }
  secret {
    name                = "aoai-primary-access-key"
    identity            = module.user_assigned_identity.user_assigned_identity_id
    key_vault_secret_id = azurerm_key_vault_secret.key_vault_secret_aoai_primary_access_key.id
  }
  template {
    container {
      name   = "real-time-backend"
      image  = var.container_image_reference
      cpu    = 0.5
      memory = "1.0Gi"
      env {
        name        = "ACS_CONNECTION_STRING"
        secret_name = "acs-connection-string"
      }
      env {
        name        = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        secret_name = "ai-connection-string"
      }
      env {
        name  = "AZURE_OPENAI_ENDPOINT"
        value = module.ai_service.cognitive_account_endpoint
      }
      env {
        name        = "AZURE_OPENAI_API_KEY"
        secret_name = "aoai-primary-access-key"
      }
    }
    http_scale_rule {
      name                = "http-scale-rule"
      concurrent_requests = 50
    }
    min_replicas                     = 1
    max_replicas                     = 10
    revision_suffix                  = "real-time-backend"
    termination_grace_period_seconds = 10
  }
  workload_profile_name = "Consumption"
}
