export type Team = {
  id: string;
  name: string;
};

export type TeamQueryInput = {
  id: string;
};

export type GetTeamResponseBody = {
  team: Team;
};
