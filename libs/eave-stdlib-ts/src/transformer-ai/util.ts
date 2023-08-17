import OpenAIClient, { formatprompt, OpenAIModel } from './openai.js';

/**
 * Given a `content` string to summarize that is (assumed) longer than `threshold`
 * tokens (as defined by the AI model), break `content` into digestable chunks,
 * summarizing and integrating each chunk into a single "rolling" summary.
 * If `content` length < `threshold`, returns `content` unchanged.
 *
 * @param client ai transformer client for summarizing text
 * @param content a (potentially) long text that must be summarized in chunks to fit the AI model token limit
 * @param threshold max number of tokens to feed to AI per request. Note that model response size (in tokens) is equal to MAX_TOKENS - threshold.
 *                  Defaults to MAX_TOKENS / 2.
 *                  (Recommended to be less than MAX_TOKENS allowed by API)
 * @return a summary of the content in `content`
 */
export async function rollingSummary(
  client: OpenAIClient,
  content: string,
  threshold: number | undefined = undefined,
  model: OpenAIModel = OpenAIModel.GPT4,
): Promise<string> {
  const chunkSize = threshold === undefined ? Math.floor(OpenAIClient.maxTokens(model) / 2) : threshold;
  let summary = content;

  while (OpenAIClient.tokenCount(summary, model) > chunkSize) {
    let newSummary = summary;
    let currPosition = 0;
    let currChunk = summary.slice(currPosition, currPosition + chunkSize);
    const chunks = [currChunk];

    // Break `summary` into strings of `chunkSize` tokens.
    // There are generally 0.75 words per token, so approximating 1 character per token may
    // be overly generous in some contexts, but it's a safe minimum.
    // cite: https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    while (currChunk.length === chunkSize) {
      currPosition += chunkSize;
      currChunk = summary.slice(currPosition, currPosition + chunkSize);
      chunks.push(currChunk);
    }

    // summarize each chunk, combining it into existing summary
    for (const chunk of chunks.filter((chnk) => chnk.length > 0)) {
      let prompt: string;
      if (newSummary.length === 0) {
        prompt = formatprompt(
          'Condense the following information. Maintain the important information.\n',
          '###',
          chunk,
          '###',
        );
      } else {
        prompt = formatprompt(
          'Amend and expand on the following information. Maintain the important information.\n\n',
          '###',
          newSummary,
          '\n',
          chunk,
          '###',
        );
      }

      newSummary = await client.createChatCompletion({
        parameters: {
          messages: [
            { role: 'user', content: prompt },
          ],
          model,
          temperature: 0.9,
          frequency_penalty: 1,
          presence_penalty: 1,
        },
      });
    }

    summary = newSummary;
  }

  return summary;
}
