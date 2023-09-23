export type GithubInstallationInput = {
  github_install_id: string;
};

export type GithubInstallation = {
  id: string;
  /** eave TeamOrm model id */
  team_id: string;
  github_install_id: string;
};
