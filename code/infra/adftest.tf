module "data_factory" {
  source = "github.com/PerfectThymeTech/terraform-azurerm-modules//modules/datafactory?ref=main"
  providers = {
    azurerm = azurerm
    azapi   = azapi
    time    = time
  }

  location                       = var.location
  resource_group_name            = azurerm_resource_group.resource_group.name
  tags                           = var.tags
  data_factory_name              = "tftst-mabuss-adf001"
  data_factory_purview_id        = null
  data_factory_azure_devops_repo = {}
  data_factory_github_repo       = {}
  data_factory_global_parameters = {}
  data_factory_published_content = {
    # parameters_file = "./tests/adf/ARMTemplateParametersForFactory.json"
    # template_file   = "./tests/adf/ARMTemplateForFactory.json"
  }
  data_factory_published_content_template_variables = {
    # data_factory_name = "tftst-mabuss-adf001"
  }
  data_factory_triggers_start = []
  data_factory_pipelines_run  = []
  data_factory_managed_private_endpoints = {
    # "storage-test" = {
    #   subresource_name   = "blob"
    #   target_resource_id = "/subscriptions/1fdab118-1638-419a-8b12-06c9543714a0/resourceGroups/tfmodule-test-rg/providers/Microsoft.Storage/storageAccounts/mytfteststg"
    # }
  }
  diagnostics_configurations       = []
  subnet_id                        = azapi_resource.subnet_private_endpoints.id
  private_dns_zone_id_data_factory = "/subscriptions/e82c5267-9dc4-4f45-ac13-abdd5e130d27/resourceGroups/ptt-dev-privatedns-rg/providers/Microsoft.Network/privateDnsZones/privatelink.datafactory.azure.net"
  customer_managed_key             = var.customer_managed_key
}

resource "azurerm_data_factory_integration_runtime_azure" "data_factory_integration_runtime_azure" {
  data_factory_id = module.data_factory.data_factory_id

  name     = "mabuss-azure-ir001"
  location = var.location

  description             = "Azure Integration Runtime for Data Factory used in Terraform testing"
  cleanup_enabled         = false
  compute_type            = "General"
  core_count              = 8
  time_to_live_min        = 120
  virtual_network_enabled = true
}

resource "azapi_update_resource" "data_factory_integration_runtime_azure_update" {
  type        = "Microsoft.DataFactory/factories/integrationRuntimes@2018-06-01"
  resource_id = azurerm_data_factory_integration_runtime_azure.data_factory_integration_runtime_azure.id

  body = {
    properties = {
      computeProperties = {
        copyComputeScaleProperties = {
          dataIntegrationUnit = 64
          timeToLive          = 30
        }
        # maxParallelExecutionsPerNode = 1
        # nodeSize = "string"
        # numberOfNodes = 2
        pipelineExternalComputeScaleProperties = {
          numberOfExternalNodes = 2
          numberOfPipelineNodes = 2
          timeToLive            = 30
        }
      }
    }
  }
}
