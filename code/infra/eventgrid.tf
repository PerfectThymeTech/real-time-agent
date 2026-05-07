resource "azurerm_eventgrid_system_topic" "eventgrid_system_topic" {
  name                = "${module.communication_service.communication_service_name}-egst001"
  resource_group_name = azurerm_resource_group.resource_group.name
  location            = "global"

  source_resource_id = module.communication_service.communication_service_id
  topic_type         = "Microsoft.Communication.CommunicationServices"
}

resource "azurerm_eventgrid_system_topic_event_subscription" "eventgrid_system_topic_event_subscription" {
  name                = "event-subscription-phonecall"
  system_topic        = azurerm_eventgrid_system_topic.eventgrid_system_topic.name
  resource_group_name = azurerm_resource_group.resource_group.name

  advanced_filtering_on_arrays_enabled = true
  event_delivery_schema                = "EventGridSchema"
  included_event_types = [
    "Microsoft.Communication.IncomingCall",
  ]
  labels = []
  retry_policy {
    event_time_to_live    = 1440
    max_delivery_attempts = 30
  }
  webhook_endpoint {
    url                               = "https://${azurerm_container_app_environment.container_app_environment.default_domain}/v1/calls/incoming"
    max_events_per_batch              = 1
    preferred_batch_size_in_kilobytes = 64
    # active_directory_tenant_id        = data.azurerm_client_config.current.tenant_id
    # active_directory_app_id_or_uri    = "" # TODO: Add the App ID URI of the AAD App used by the Container App
  }
}
