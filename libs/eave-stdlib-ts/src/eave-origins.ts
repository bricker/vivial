import { InvalidEnumCase } from "./exceptions.js";

export enum EaveApp {
  eave_api = "eave_api",
  eave_dashboard = "eave_dashboard",
  eave_github_app = "eave_github_app",
}

export function appengineServiceName(eaveApp: EaveApp): string {
  switch (eaveApp) {
    case EaveApp.eave_api:
      return "api";
    case EaveApp.eave_dashboard:
      return "dashboard";
    case EaveApp.eave_github_app:
      return "github";
    default:
      throw new InvalidEnumCase(eaveApp);
  }
}

export enum ExternalOrigin {
  github_api_client = "github_api_client",
}
