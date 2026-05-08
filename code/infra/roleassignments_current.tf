# Key Vault Role Assignments
resource "azurerm_role_assignment" "current_role_assignment_key_vault_secrets_officer" {
  description          = "Required for the deployment to create secrets in the key vault."
  scope                = module.key_vault.key_vault_id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}
