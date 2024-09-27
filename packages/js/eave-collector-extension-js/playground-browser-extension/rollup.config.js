import path from "node:path";
import { nodeResolve } from "@rollup/plugin-node-resolve";

export default {
  input: "./background/service-worker.js",
  output: [
    {
      file: path.resolve(".", "dist", "background.js"),
      format: "iife",
      // name: "PlaygroundExtension"
    }
  ],
  context: "this",
  plugins: [
    nodeResolve(),
  ],
};

