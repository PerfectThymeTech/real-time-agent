# Key Vault Role Assignments
resource "azurerm_role_assignment" "uai_role_assignment_key_vault_secrets_user" {
  description          = "Required for the container app to access secrets in the key vault."
  scope                = module.key_vault.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

# Cognitive Services OpenAI Role Assignments
resource "azurerm_role_assignment" "uai_role_assignment_ai_service_cognitive_services_openai_user" {
  description          = "Required for accessing azure open ai models from the container app."
  scope                = module.ai_service.cognitive_account_id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}

# Application Insights role assignments
resource "azurerm_role_assignment" "uai_role_assignment_application_insights_monitoring_metrics_publisher" {
  description          = "Required for publishing logs in the application insights instance from the web app app settings."
  scope                = module.application_insights.application_insights_id
  role_definition_name = "Monitoring Metrics Publisher"
  principal_id         = module.user_assigned_identity.user_assigned_identity_principal_id
  principal_type       = "ServicePrincipal"
}
