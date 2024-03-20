// TODO: need access to list of fields; but that's not in the ORM yet
export type VirtualEvent = {
  id: string;
  readable_name: string;
  description?: string;
};

export type VirtualEventQueryInput = {
  search_term: string;
};
