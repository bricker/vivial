// TODO: need access to list of fields; but that's not in the ORM yet
export type VirtualEvent = {
  id: string;
  readable_name: string;
  description?: string;
  fields?: string[];
};

export type VirtualEventQueryInput = {
  search_term: string;
};

export type GetVirtualEventsRequestBody = {
  virtual_events?: VirtualEventQueryInput;
};

export type GetVirtualEventsResponseBody = {
  virtual_events: Array<VirtualEvent>;
};
