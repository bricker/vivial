import { myWindow } from "../types/window";

export const CORE_API_INTERNAL_BASE = myWindow.app.apiBase;
export const ADMIN_GRAPHQL_API_BASE = `${CORE_API_INTERNAL_BASE}/internal/graphql`;
