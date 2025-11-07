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
  cognitive_account_local_auth_enabled                    = true
  cognitive_account_deployments                           = {}
  diagnostics_configurations                              = local.diagnostics_configurations
  subnet_id                                               = azapi_resource.subnet_private_endpoints.id
  connectivity_delay_in_seconds                           = var.connectivity_delay_in_seconds
  private_dns_zone_id_cognitive_account                   = var.private_dns_zone_id_open_ai
  customer_managed_key                                    = var.customer_managed_key
}

resource "azurerm_cognitive_account_rai_policy" "cognitive_account_rai_policy" {
  name                 = "default"
  cognitive_account_id = module.ai_service.cognitive_account_id

  base_policy_name = "Microsoft.DefaultV2"
  content_filter {
    name               = "Violence"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Prompt"
  }
  content_filter {
    name               = "Hate"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Prompt"
  }
  content_filter {
    name               = "Sexual"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Prompt"
  }
  content_filter {
    name               = "Selfharm"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Prompt"
  }
  content_filter {
    name               = "Jailbreak"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Prompt"
  }
  content_filter {
    name               = "Indirect Attack"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Prompt"
  }
  content_filter {
    name               = "Indirect Attack Spotlighting"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Prompt"
  }
  content_filter {
    name               = "Violence"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Completion"
  }
  content_filter {
    name               = "Hate"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Completion"
  }
  content_filter {
    name               = "Sexual"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Completion"
  }
  content_filter {
    name               = "Selfharm"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Completion"
  }
  content_filter {
    name               = "Protected Material Text"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Completion"
  }
  content_filter {
    name               = "Protected Material Code"
    filter_enabled     = false
    block_enabled      = false
    severity_threshold = "Medium"
    source             = "Completion"
  }
  mode = "Asynchronous_filter"

  depends_on = [
    module.ai_service.cognitive_account_setup_completed
  ]
}

resource "azurerm_cognitive_deployment" "cognitive_deployment_gpt_realtime" {
  name                 = "gpt-realtime"
  cognitive_account_id = module.ai_service.cognitive_account_id

  model {
    format  = "OpenAI"
    name    = "gpt-realtime"
    version = "2025-08-28"
  }
  rai_policy_name = azurerm_cognitive_account_rai_policy.cognitive_account_rai_policy.name
  sku {
    name     = "GlobalStandard"
    capacity = 100
  }
  version_upgrade_option = "OnceCurrentVersionExpired"

  depends_on = [
    module.ai_service.cognitive_account_setup_completed
  ]
}

resource "azurerm_cognitive_deployment" "cognitive_deployment_gpt_40_transcribe" {
  name                 = "gpt-4o-transcribe"
  cognitive_account_id = module.ai_service.cognitive_account_id

  model {
    format  = "OpenAI"
    name    = "gpt-4o-transcribe"
    version = "2025-03-20"
  }
  rai_policy_name = azurerm_cognitive_account_rai_policy.cognitive_account_rai_policy.name
  sku {
    name     = "GlobalStandard"
    capacity = 100
  }
  version_upgrade_option = "OnceCurrentVersionExpired"

  depends_on = [
    module.ai_service.cognitive_account_setup_completed
  ]
}
