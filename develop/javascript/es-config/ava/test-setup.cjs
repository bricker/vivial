const { loadStandardDotenvFiles, populateEnv } = require("../../dotenv-loader.cjs");

populateEnv({ EAVE_ENV: "test" });
loadStandardDotenvFiles();
