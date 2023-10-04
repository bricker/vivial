export type SlackInstallationInput = {
  slack_team_id: string;
};

export type SlackInstallation = {
  id: string;
  /** eave TeamOrm model id */
  team_id: string;
  slack_team_id: string;
  bot_token: string;
  bot_id: string;
  bot_user_id: string | null;
};
