import { applyShutdownHandlers } from "@eave-fyi/eave-stdlib-ts/src/api-util.js";
import { app } from "./src/app.js";

const PORT = parseInt(process.env["PORT"] || "5300", 10);
const server = app.listen(PORT, "0.0.0.0", async () => {
  console.info(`App listening on port ${PORT}`, process.env["NODE_ENV"]);
});

applyShutdownHandlers({ server });
