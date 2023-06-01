
export enum EaveForgeInboundOperation {
  createDocument = 'createDocument',
  updateDocument = 'updateDocument',
  archiveDocument = 'archiveDocument',

}

export type ForgeInstallation = {
  id: string;
  forge_app_id: string;
  forge_app_version: string;
  forge_app_installation_id: string;
  forge_app_installer_account_id: string;
  webtrigger_url: string;
  confluence_space_key?: string;
}

export type QueryForgeInstallationInput = {
  forge_app_id: string;
  forge_app_installation_id: string;
}
export type RegisterForgeInstallationInput = {
  forge_app_id: string;
  forge_app_version: string;
  forge_app_installation_id: string;
  forge_app_installer_account_id: string;
  webtrigger_url: string;
  confluence_space_key?: string;
}

export type UpdateForgeInstallationInput = {
  forge_app_installation_id: string;
  forge_app_version?: string;
  forge_app_installer_account_id?: string;
  webtrigger_url?: string;
  confluence_space_key?: string;
}