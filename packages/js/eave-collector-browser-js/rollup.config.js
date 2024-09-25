import typescript from "@rollup/plugin-typescript";
import path from "node:path";
import terser from "@rollup/plugin-terser";
import replace from "@rollup/plugin-replace";

const trackerUrl = process.env.EAVE_API_BASE_URL || "https://api.eave.fyi";
const mode = process.env.MODE;
const isDevelopment = mode === "development";
const name = "EaveBrowserCollector";

export default {
  input: "./src/main.ts",
  output: [
    {
      file: path.resolve(".", "dist", "collector.js"),
      format: "es",
      name,
      sourcemap: isDevelopment,
    },
    {
      file: path.resolve(".", "dist", "collector.min.js"),
      format: "iife",
      name,
      plugins: [
        !isDevelopment && terser({
          mangle: true,
          compress: {
            drop_console: !isDevelopment ? ["debug"] : false,
          },
          format: {
            comments: false,
            ecma: 2015,
          },
        }),
      ]
    }
  ],
  plugins: [
    typescript(),
    replace({
      preventAssignment: true,
      values: {
        WEBPACK_ENV_EAVE_API_BASE_URL: JSON.stringify(trackerUrl),
        WEBPACK_ENV_MODE: JSON.stringify(mode),
      },
    }),
  ],
};

