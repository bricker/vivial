

























function guessExpressAPIName(rootDir: string): string {
  const dirName = path.basename(rootDir);
  const apiName = dirName.replace(/[^a-zA-Z0-9]/g, ' ').toUpperCase();
  const apiRegex = new RegExp("API");
  if (apiRegex.test(apiName)) {
    return apiName;
  }
  return apiName + " API";
}







// TODO: dynamically determine language (ts vs js)
// async function generateExpressAPIDoc(apiEndpoints: Array<string>): Promise<string> {
//   let apiDoc = "";
//   for (const apiEndpoint of apiEndpoints) {
//     const openaiClient = await OpenAIClient.getAuthedClient();
//     const systemPrompt = formatprompt(`
//       You will be given a block of TypeScript code, delimited by three exclamation marks, containing definitions for API endpoints using the Express API framework.

//       Your task is to generate API documentation for the provided Express REST API endpoint.

//       Use the following template to format your response:

//       ## {description of the API endpoint in 3 words or less}

//       \`\`\`
//       {HTTP Method} {Path}
//       \`\`\`

//       {high-level description of what the API endpoint does}

//       ### Path Parameters

//       **{name}** ({type}) *{optional or required}* - {description}

//       ### Example Request

//       \`\`\`
//       {example request}
//       \`\`\`

//       ### Example Response

//       \`\`\`
//       {example response}
//       \`\`\`

//       ### Response Codes

//       **{response code}**: {explanation of when this response code will be returned}

//     `);
//     const userPrompt = formatprompt(`
//       !!!
//       ${apiEndpoint}
//     `);
//     const openaiResponse = await openaiClient.createChatCompletion({
//       parameters: {
//         messages: [
//           { role: 'system', content: systemPrompt },
//           { role: 'user', content: userPrompt },
//         ],
//         model: OpenAIModel.GPT4,
//       },
//     });
//     if (openaiResponse) {
//       apiDoc += `${openaiResponse}\n\n<br />\n\n`;
//     }
//   }
//   return apiDoc;
// }





function getParser(fileExt: string): Parser {
  return new Parser();
}












// TODO: REMOVE
documentExpressAPIs();

