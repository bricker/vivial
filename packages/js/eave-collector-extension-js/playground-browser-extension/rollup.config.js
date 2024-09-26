import path from "node:path";

export default {
  input: "./background/service-worker.js",
  output: [
    {
      file: path.resolve(".", "dist", "background.js"),
      format: "iife",
      // name: "PlaygroundExtension"
    }
  ],
};

