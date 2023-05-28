export type ForgeInstallation = {
  id: string;
  forge_app_id: string;
  forge_app_version: string;
  forge_app_installation_id: string;
  forge_app_installer_account_id: string;
  confluence_space_key?: string;
}
export type ForgeWebTrigger = {
  id: string;
  webtrigger_key: string;
  webtrigger_url: string;
}
