export type ConfluenceSpace = {
  key: string;
  name: string;
};

export type AtlassianInstallation = {
  id: string;
  /** eave TeamOrm model id */
  team_id: string;
  atlassian_cloud_id: string;
  confluence_space: string | null;
  available_confluence_spaces: Array<ConfluenceSpace> | null;
};

// Typealias for naming consistency
export type AtlassianInstallationPeek = AtlassianInstallation;
