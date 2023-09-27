import dotenv from "dotenv";
import path from "node:path";

dotenv.config({ path: path.join(process.env["EAVE_HOME"], ".env") });

try {
  dotenv.config({
    path: path.join(process.env["EAVE_HOME"], ".env.test"),
    override: true,
  });
} catch (e) {
  console.warn(".env.test file not found");
}

dotenv.populate(
  process.env,
  {
    EAVE_MONITORING_DISABLED: "1",
    EAVE_ANALYTICS_DISABLED: "1",
    EAVE_API_BASE_PUBLIC: "https://api.eave.tests",
    EAVE_APPS_BASE_PUBLIC: "https://apps.eave.tests",
    EAVE_WWW_BASE_PUBLIC: "https://www.eave.tests",
    EAVE_COOKIE_DOMAIN: ".eave.tests",
  },
  { override: true },
);
