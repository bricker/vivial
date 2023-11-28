import { promises as fs } from "node:fs";
import OpenAI from "openai";
import { sharedConfig } from "./config.js";
import { formatprompt } from "./transformer-ai/openai.js";
import { ChatCompletionChunk } from "openai/resources/index.js";

const SEED = 10197118101;

async function main() {
  const code = await fs.readFile(
    "../../apps/core/eave/core/public/requests/oauth/github_oauth.py",
    "utf-8",
  );

  const openai = new OpenAI({
    apiKey: await sharedConfig.openaiApiKey,
  });

  const stream = await openai.chat.completions.create({
    stream: true,
    seed: SEED,
    model: "gpt-4-1106-preview",
    messages: [
      {
        role: "user",
        content: formatprompt(
          "Analyze this code and create a flowchart of the logic.",
          "###",
          code.toString(),
          "###",
        ),
      },
    ],
  });

  let lastChunk: ChatCompletionChunk | undefined;

  for await (const chunk of stream) {
    const choice = chunk.choices[0];
    const content = choice?.delta.content;
    if (content) {
      process.stdout.write(content);
    }

    if (choice?.finish_reason !== null) {
      lastChunk = chunk;
    }
  }

  console.log("\n");
  console.dir(lastChunk);
}

void main();
