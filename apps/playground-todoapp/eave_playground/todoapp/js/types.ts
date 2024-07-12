export type TodoListItem = {
  id: string;
  user_id: string;
  text: string;
  created: string;
  updated: string | null;
};

export type TodoSummary = {
  text: string;
};
