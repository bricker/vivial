// run this dummy script with
// npx tsx libs/eave-stdlib-ts/src/code-trace-analysis/code-analysis.ts

import crypto from "crypto";
import Parser from "tree-sitter";
import { LogContext } from "../logging.js";
import { grammarForFilePathOrName } from "../parsing/grammars.js";
import { OpenAIModel } from "../transformer-ai/models.js";
import OpenAIClient, { formatprompt } from "../transformer-ai/openai.js";

const funcs = [
  // String.raw`export async function runApiDocumentationTaskHandler(
  //   req: Express.Request,
  //   res: Express.Response,
  // ): Promise<void> {
  //   const ctx = LogContext.load(res);
  //   ctx.feature_name = "api_documentation";
  //   eaveLogger.debug("API documentation task started", { input: req.body }, ctx);

  //   const input = <RunApiDocumentationTaskRequestBody>req.body;
  //   const sharedAnalyticsParams: { [key: string]: JsonValue } = {};
  //   ctx.set({ sharedAnalyticsParams });

  //   const teamId = req.header(EAVE_TEAM_ID_HEADER);
  //   if (!teamId) {
  //     throw new MissingRequiredHeaderError(EAVE_TEAM_ID_HEADER);
  //   }

  //   const coreAPIData = new CoreAPIData({
  //     teamId,
  //     ctx,
  //     externalRepoId: input.repo.external_repo_id,
  //   });
  //   sharedAnalyticsParams["core_api_data"] = coreAPIData.logParams;
  //   const eaveTeam = await coreAPIData.getTeam();
  //   ctx.set({ eave_team: eaveTeam });

  //   eaveLogger.debug("eave core API data", sharedAnalyticsParams, ctx);

  //   const eaveGithubRepo = await coreAPIData.getEaveGithubRepo();
  //   assert(
  //     eaveGithubRepo.api_documentation_state === GithubRepoFeatureState.ENABLED,
  //     \`API documentation feature not enabled for repo ID \${eaveGithubRepo.external_repo_id}\`,
  //   );

  //   const installId = await getInstallationId(eaveTeam.id, ctx);
  //   assert(installId, \`No github integration found for team ID \${eaveTeam.id}\`);

  //   const octokit = await createOctokitClient(installId);

  //   let jobResult = LastJobResult.none;
  //   try {
  //     const githubAPIData = new GithubAPIData({
  //       ctx,
  //       octokit,
  //       externalRepoId: eaveGithubRepo.external_repo_id,
  //     });
  //     sharedAnalyticsParams["github_data"] = githubAPIData.logParams;

  //     const externalGithubRepo = await githubAPIData.getExternalGithubRepo();
  //     if (externalGithubRepo.isEmpty) {
  //       res.sendStatus(200);
  //       return;
  //     }

  //     if (!input.force) {
  //       const existingGithubDocuments = await coreAPIData.getGithubDocuments();
  //       // If there aren't any associated github documents yet, always run the task.
  //       if (
  //         existingGithubDocuments &&
  //         Object.keys(existingGithubDocuments).length > 0
  //       ) {
  //         const latestCommitOnDefaultBranch =
  //           await githubAPIData.getLatestCommitOnDefaultBranch();
  //         if (latestCommitOnDefaultBranch) {
  //           const committedDate = Date.parse(
  //             latestCommitOnDefaultBranch.committedDate,
  //           );
  //           const oneDayAgo = Date.now() - 1000 * 60 * 60 * 24;
  //           if (committedDate < oneDayAgo) {
  //             eaveLogger.debug(
  //               "API doc task skipped due to delta check",
  //               sharedAnalyticsParams,
  //               ctx,
  //             );
  //             res.sendStatus(200);
  //             return;
  //           }
  //         }
  //       }
  //     }

  //     // indicate in db that this job is processing
  //     await UpsertApiDocumentationJobOperation.perform({
  //       teamId,
  //       origin: appConfig.eaveOrigin,
  //       input: {
  //         job: {
  //           github_repo_id: eaveGithubRepo.id,
  //           state: ApiDocumentationJobState.running,
  //         },
  //       },
  //       ctx,
  //     });

  //     const expressRootDirs = await githubAPIData.getExpressRootDirs();
  //     if (expressRootDirs.length === 0) {
  //       eaveLogger.warning(
  //         "no express apps detected",
  //         sharedAnalyticsParams,
  //         ctx,
  //       );

  //       res.sendStatus(200);
  //       jobResult = LastJobResult.no_api_found;
  //       return;
  //     }

  //     eaveLogger.debug("express apps detected", sharedAnalyticsParams, ctx);

  //     const results = await Promise.allSettled(
  //       expressRootDirs.map(async (apiRootDir) => {
  //         try {
  //           const localAnalyticsParams: { [key: string]: JsonValue } = {};
  //           localAnalyticsParams["api_root_dir"] = apiRootDir;

  //           eaveLogger.debug(
  //             "building documentation",
  //             localAnalyticsParams,
  //             sharedAnalyticsParams,
  //             ctx,
  //           );

  //           const expressAPIInfo = await ExpressAPIDocumentBuilder.buildAPI({
  //             githubAPIData,
  //             coreAPIData,
  //             apiRootDir,
  //             ctx,
  //           });
  //           assertPresence(expressAPIInfo);

  //           expressAPIInfo.documentationFilePath = documentationFilePath({
  //             apiName: expressAPIInfo.name,
  //           });

  //           localAnalyticsParams["express_api_info"] = expressAPIInfo.asJSON;
  //           eaveLogger.debug(
  //             "express API info",
  //             localAnalyticsParams,
  //             sharedAnalyticsParams,
  //             ctx,
  //           );

  //           let eaveDoc = await coreAPIData.getGithubDocument({
  //             filePath: expressAPIInfo.documentationFilePath,
  //           });
  //           localAnalyticsParams["eave_doc"] = eaveDoc;

  //           if (!expressAPIInfo.rootFile) {
  //             eaveLogger.warning(
  //               "no root file found",
  //               localAnalyticsParams,
  //               sharedAnalyticsParams,
  //               ctx,
  //             );

  //             if (eaveDoc) {
  //               eaveLogger.warning(
  //                 "updating github document with status FAILED",
  //                 localAnalyticsParams,
  //                 sharedAnalyticsParams,
  //                 ctx,
  //               );

  //               await coreAPIData.updateGithubDocument({
  //                 document: eaveDoc,
  //                 newValues: { status: GithubDocumentStatus.FAILED },
  //               });
  //             }

  //             return null;
  //           }

  //           if (
  //             !expressAPIInfo.endpoints ||
  //             expressAPIInfo.endpoints.length === 0
  //           ) {
  //             eaveLogger.warning(
  //               "no express endpoints found",
  //               sharedAnalyticsParams,
  //               localAnalyticsParams,
  //               ctx,
  //             );

  //             if (eaveDoc) {
  //               eaveLogger.warning(
  //                 "updating github document with status FAILED",
  //                 sharedAnalyticsParams,
  //                 localAnalyticsParams,
  //                 ctx,
  //               );

  //               await coreAPIData.updateGithubDocument({
  //                 document: eaveDoc,
  //                 newValues: { status: GithubDocumentStatus.FAILED },
  //               });
  //             }

  //             return null;
  //           }

  //           if (eaveDoc) {
  //             eaveLogger.debug(
  //               "updating github document with status PROCESSING",
  //               sharedAnalyticsParams,
  //               localAnalyticsParams,
  //               ctx,
  //             );

  //             eaveDoc = await coreAPIData.updateGithubDocument({
  //               document: eaveDoc,
  //               newValues: { status: GithubDocumentStatus.PROCESSING },
  //             });
  //             localAnalyticsParams["eave_doc"] = eaveDoc;
  //           } else {
  //             eaveLogger.debug(
  //               "creating initial placeholder github document",
  //               sharedAnalyticsParams,
  //               localAnalyticsParams,
  //               ctx,
  //             );
  //             eaveDoc = await coreAPIData.createPlaceholderGithubDocument({
  //               apiName: expressAPIInfo.name,
  //               documentationFilePath: expressAPIInfo.documentationFilePath,
  //             });
  //             localAnalyticsParams["eave_doc"] = eaveDoc;
  //           }

  //           eaveLogger.debug(
  //             "generating API documentation from openai",
  //             sharedAnalyticsParams,
  //             localAnalyticsParams,
  //             ctx,
  //           );

  //           const newDocumentContents = await generateExpressAPIDoc({
  //             expressAPIInfo,
  //             ctx,
  //           });
  //           if (!newDocumentContents) {
  //             eaveLogger.warning(
  //               "Empty express API documentation.",
  //               sharedAnalyticsParams,
  //               localAnalyticsParams,
  //               ctx,
  //             );

  //             eaveLogger.warning(
  //               "updating github document with status FAILED",
  //               sharedAnalyticsParams,
  //               localAnalyticsParams,
  //               ctx,
  //             );

  //             await coreAPIData.updateGithubDocument({
  //               document: eaveDoc,
  //               newValues: { status: GithubDocumentStatus.FAILED },
  //             });
  //             return null;
  //           }

  //           eaveLogger.debug(
  //             "successfully generated API documentation",
  //             sharedAnalyticsParams,
  //             localAnalyticsParams,
  //             ctx,
  //           );

  //           expressAPIInfo.documentation = newDocumentContents;
  //           return expressAPIInfo;
  //         } catch (e: any) {
  //           eaveLogger.exception(e, sharedAnalyticsParams, ctx);
  //           throw e;
  //         }
  //       }),
  //     );

  //     const validExpressAPIs = results
  //       .filter((r) => r.status === "fulfilled" && r.value)
  //       .map((r) => (<PromiseFulfilledResult<ExpressAPI>>r).value);
  //     sharedAnalyticsParams["express_apis"] = validExpressAPIs.map(
  //       (e) => e.asJSON,
  //     );
  //     eaveLogger.debug("final express APIs", sharedAnalyticsParams, ctx);

  //     const fileAdditions: FileAddition[] = validExpressAPIs.map((d) => {
  //       assertPresence(d.documentation);

  //       return {
  //         path: d.documentationFilePath || "eave_docs.md", // TODO: This will drop it in the root of the project
  //         contents: Buffer.from(d.documentation).toString("base64"),
  //       };
  //     });

  //     if (fileAdditions.length === 0) {
  //       eaveLogger.warning("No file additions", sharedAnalyticsParams, ctx);
  //       eaveLogger.warning(
  //         "updating github documents with status FAILED",
  //         sharedAnalyticsParams,
  //         ctx,
  //       );
  //       await updateDocuments({
  //         coreAPIData,
  //         expressAPIs: validExpressAPIs,
  //         newValues: { status: GithubDocumentStatus.FAILED },
  //       });
  //       jobResult = LastJobResult.error;
  //       return;
  //     }

  //     const prCreator = new PullRequestCreator({
  //       repoName: externalGithubRepo.name,
  //       repoOwner: externalGithubRepo.owner.login,
  //       repoId: externalGithubRepo.id,
  //       baseBranchName: externalGithubRepo.defaultBranchRef?.name || "main", // The only reason \`defaultBranchRef\` would be undefined is if it wasn't specified in the query fields. But defaulting to "main" is easier than handling the runtime error and will work for most cases.
  //       octokit,
  //       ctx,
  //     });

  //     eaveLogger.debug("creating pull request", sharedAnalyticsParams, ctx);

  //     const pullRequest = await prCreator.createPullRequest({
  //       branchName: API_BRANCH_NAME,
  //       commitMessage: "docs: automated update",
  //       prTitle: "docs: Eave API documentation update",
  //       prBody: "Your new API docs based on recent changes to your code",
  //       fileChanges: {
  //         additions: fileAdditions,
  //       },
  //     });

  //     await updateDocuments({
  //       coreAPIData,
  //       expressAPIs: validExpressAPIs,
  //       newValues: {
  //         pull_request_number: pullRequest.number,
  //         status: GithubDocumentStatus.PR_OPENED,
  //       },
  //     });

  //     jobResult = LastJobResult.doc_created;
  //   } catch (e: unknown) {
  //     jobResult = LastJobResult.error;
  //     throw e;
  //   } finally {
  //     await UpsertApiDocumentationJobOperation.perform({
  //       teamId,
  //       origin: appConfig.eaveOrigin,
  //       input: {
  //         job: {
  //           github_repo_id: eaveGithubRepo.id,
  //           state: ApiDocumentationJobState.idle,
  //           last_result: jobResult,
  //         },
  //       },
  //       ctx,
  //     });
  //   }
  // }`,
  //   String.raw`
  // async def get(self, request: Request) -> Response:
  //     # random value for verifying request wasnt tampered with via CSRF
  //     token: str = oauthlib.common.generate_token()

  //     # For GitHub, there is a problem: The combined Installation + Authorization flow doesn't allow us
  //     # to specify a redirect_uri; it chooses the first one configured. So it always redirects to eave.fyi,
  //     # which makes it practically impossible to test in development (without some proxy configuration).
  //     # So instead, we're going to set a special cookie and read it on the other side (callback), and redirect if necessary.
  //     # https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app#generating-a-user-access-token-when-a-user-installs-your-app
  //     state_json = json.dumps({"token": token, "redirect_uri": GITHUB_OAUTH_CALLBACK_URI})
  //     state = eave.stdlib.util.b64encode(state_json, urlsafe=True)

  //     authorization_url = f"{SHARED_CONFIG.eave_github_app_public_url}/installations/new?state={state}"
  //     # authorization_url = f"https://github.com/login/oauth/authorize?{qp}"
  //     response = RedirectResponse(url=authorization_url)

  //     utm_cookies.set_tracking_cookies(
  //         response=response,
  //         request=request,
  //     )

  //     oauth_cookies.save_state_cookie(
  //         response=response,
  //         state=state,
  //         provider=_AUTH_PROVIDER,
  //     )

  //     return response
  // `,
  //   String.raw`
  // async def get(
  //     self,
  //     request: Request,
  // ) -> Response:
  //     self.response = Response()
  //     self.eave_state = EaveRequestState.load(request=request)

  //     if "state" not in request.query_params and "code" not in request.query_params:
  //         # unable to check validity of data received. or could just be a
  //         # permissions update from gh website redirecting to our callback
  //         shared.set_redirect(
  //             response=self.response,
  //             location=shared.DEFAULT_REDIRECT_LOCATION,
  //         )
  //         return self.response

  //     if "state" in request.query_params:
  //         # we set this state in our /oauth/github/authorize endpoint before handing
  //         # auth over to github
  //         self.state = state = request.query_params["state"]

  //         # Because of the GitHub redirect_uri issue described in this file, we need to get the redirect_uri from state,
  //         # and redirect if it's on a different host.
  //         # Reminder that in this scenario, the cookies from your local environment won't be available here (because we're probably at eave.fyi)
  //         state_decoded = json.loads(eave.stdlib.util.b64decode(state, urlsafe=True))
  //         if redirect_uri := state_decoded.get("redirect_uri"):
  //             url = urllib.parse.urlparse(redirect_uri)
  //             if url.hostname != request.url.hostname:
  //                 qp = urllib.parse.urlencode(request.query_params)
  //                 location = f"{redirect_uri}?{qp}"
  //                 return shared.set_redirect(response=self.response, location=location)

  //         shared.verify_oauth_state_or_exception(
  //             state=self.state, auth_provider=_AUTH_PROVIDER, request=request, response=self.response
  //         )

  //     if "code" in request.query_params:
  //         # github marketplace installs skip the step where we set state, so manually
  //         # validate the user (oauth code) has access to the app installation
  //         installation_id = request.query_params.get("installation_id")
  //         code = request.query_params.get("code")
  //         if not installation_id or not code:
  //             eaveLogger.warning(
  //                 "Missing GitHub user oauth code and/or app installation_id. Cannot proceed.",
  //                 self.eave_state.ctx,
  //             )
  //             return shared.cancel_flow(response=self.response)

  //         await shared.verify_stateless_installation_or_exception(code, installation_id, self.eave_state.ctx)

  //     setup_action = request.query_params.get("setup_action")
  //     if setup_action not in ["install", "update"]:
  //         eaveLogger.warning(f"Unexpected github setup_action: {setup_action}", self.eave_state.ctx)

  //     installation_id = request.query_params.get("installation_id")
  //     if not installation_id:
  //         eaveLogger.warning(
  //             f"github installation_id not provided for action {setup_action}. Cannot proceed.",
  //             self.eave_state.ctx,
  //         )
  //         return shared.cancel_flow(response=self.response)

  //     self.installation_id = installation_id
  //     auth_cookies = get_auth_cookies(cookies=request.cookies)

  //     try:
  //         await self._maybe_set_account_data(auth_cookies)
  //         await self._update_or_create_github_installation()
  //         # dont link github repos to our db until we know what team to associate them w/
  //         if self._request_logged_in():
  //             assert self.eave_team  # make types happy
  //             await shared.sync_github_repos(team_id=self.eave_team.id, ctx=self.eave_state.ctx)
  //     except Exception as e:
  //         if shared.is_error_response(self.response):
  //             return self.response
  //         raise e

  //     return self.response
  // `,

  //   String.raw`
  // async def _maybe_set_account_data(self, auth_cookies: AuthCookies) -> None:
  //     if not auth_cookies.all_set:
  //         # This is the case where they're going through the install flow but not logged in.
  //         # (e.g. installing from github marketplace w/o an Eave account)
  //         shared.set_redirect(
  //             response=self.response,
  //             location=shared.SIGNUP_REDIRECT_LOCATION,
  //         )
  //     else:
  //         async with database.async_session.begin() as db_session:
  //             eave_account = await AccountOrm.one_or_none(
  //                 session=db_session,
  //                 params=AccountOrm.QueryParams(
  //                     id=eave.stdlib.util.ensure_uuid(auth_cookies.account_id), access_token=auth_cookies.access_token
  //                 ),
  //             )

  //             if not eave_account:
  //                 shared.cancel_flow(response=self.response)
  //                 raise Exception("auth_cookies did not point to valid account")

  //             self.eave_account = eave_account
  //             self.eave_team = await self.eave_account.get_team(session=db_session)

  //         shared.set_redirect(
  //             response=self.response,
  //             location=shared.DEFAULT_REDIRECT_LOCATION,
  //         )
  // `,

  String.raw`
async def _update_or_create_github_installation(
    self,
) -> None:
    async with database.async_session.begin() as db_session:
        # try fetch existing github installation
        github_installation_orm = await GithubInstallationOrm.query(
            session=db_session,
            params=GithubInstallationOrm.QueryParams(
                team_id=self.eave_team.id if self.eave_team else None,
                github_install_id=self.installation_id,
            ),
        )

        if not github_installation_orm:
            # create state cookie we can use later to associate new accounts
            # with a dangling app installation row
            state = None

            # only set state cookie for installations that wont have a team_id set
            if not self._request_logged_in():
                state = shared.generate_and_set_state_cookie(
                    response=self.response, installation_id=self.installation_id
                )

            # create new github installation associated with the TeamOrm
            # (or create a dangling installation to later associate w/ a future account)
            github_installation_orm = await GithubInstallationOrm.create(
                session=db_session,
                team_id=self.eave_account.team_id if self.eave_account else None,
                github_install_id=self.installation_id,
                install_flow_state=state,
            )

        elif self.eave_account and github_installation_orm.team_id != self.eave_account.team_id:
            eaveLogger.warning(
                f"A Github integration already exists with github install id {self.installation_id}",
                self.eave_state.ctx,
            )
            shared.set_error_code(response=self.response, error_code=EaveOnboardingErrorCode.already_linked)
            raise Exception("Attempted to link Github integration when one already existed")

        else:
            print("just testing")

        self.github_installation_orm = github_installation_orm
`,

  //   String.raw`
  // def _request_logged_in(self) -> bool:
  //     return self.eave_team is not None and self.eave_account is not None
  // `,
];

async function main(): Promise<void> {
  const openaiClient = await OpenAIClient.getAuthedClient();
  const model = OpenAIModel.GPT4;
  const ctx = new LogContext();

  /*
  for each function, 
    parse out whole body (+ any docs if available)
    w/in func find root level loop/condition blocks

    for each capture chunk
      gpt summary
      record code point identifier
  */
  for (const f of funcs) {
    console.log(`=======\n${f}\n========`);

    // TODO: tweak POI finding to be better
    // e.g. maybe include loops, but probs dont want to fire on each loop iter (thats a lot)
    const parser = new Parser();
    const languageGrammar = grammarForFilePathOrName("placeholder.py");
    if (!languageGrammar) {
      //   eaveLogger.debug(`No grammar found for lang`, ctx);
      console.log("no grammar found");
      continue;
    }
    parser.setLanguage(languageGrammar);
    const ptree = parser.parse(f);

    // console.log(ptree.rootNode.toString());

    // captures (python specific) if/elif/else code blocks (not including conditions)
    const query = new Parser.Query(languageGrammar,
      `(if_statement [
        consequence: (_) @cons
        alternative: (_) @alt
      ])`
    );
    const matches = query.matches(ptree.rootNode);

    const caps: string[] = [];
    matches?.forEach((qmatch: Parser.QueryMatch) => {
      console.log("got a match", qmatch);
      qmatch.captures.forEach((cap: Parser.QueryCapture) => {
        const conditionalCap = f.slice(cap.node.startIndex, cap.node.endIndex);
        const lineNum = cap.node.startPosition.row;
        console.log(cap.node.toString())
        console.log(conditionalCap)
        console.log(lineNum)
        console.log("\n=== sep ===\n");

        // TODO: narrow cap range to 1 line (start or end?) to use in UID hash

        caps.push(conditionalCap);
      });
    });

    return;
    for (const cap of caps) {
      // get summary
      const summ = await getSummary({
        openaiClient,
        model,
        ctx,
        content: cap,
        fullContext: f,
      });

      console.log(cap);
      console.log(summ);
      console.log("\n=== sep ===\n");
    }
  }
}

/**
 * TODO: get name and description for event
 * TODO: find UID for event that can be gotten from interpreter
 *
 * @returns good info
 */
async function getSummary({
  openaiClient,
  model,
  ctx,
  content,
  fullContext,
}: {
  openaiClient: OpenAIClient;
  model: OpenAIModel;
  ctx: LogContext;
  content: string;
  fullContext: string;
}): Promise<string> {
  // return "todo";

  // get summary of code and its actions
  const prompt = formatprompt(`
    Write 3 sentences or less summarizing the following code snippet. Be concise, keep your summary abstract 
    (don't specifically name variables or classes from the code), and limit your summary to just this snippet.

    \`\`\`
    ${content}
    \`\`\`
    `,
    // This gives better step summaries, but impossible to go from random step to exact code positions..
    // `
    // \`\`\`
    // ${fullContext}
    // \`\`\`
    // Write a summary document of the actions taken by the above function.
    // Be succinct, excluding redundant or unnecessary terms like "This function ...".
    // Do not include surrounding markdown-style backticks.
    // 1. 
    // `,
  );

  const response = await openaiClient.createChatCompletion({
    parameters: {
      messages: [
        // { // is this actually making the responses worse???
        //   role: "system",
        //   content: `Use this code as context to answer any following questions:\n${fullContext}`,
        // },
        {
          role: "user",
          content: prompt,
        },
      ],
      model,
      temperature: 0,
    },
    ctx,
  });

  return response;
}

// NOTE: there is a small risk of UID collision if 2 functions happen to hash to the same strings (and the coliding line number is <= len of both functions)
function buildUid(funcBody: string, relativeLineNum: number): string {
  // sha1 chosen for speed of hash to avoid bottlenecking interpreter at code execution time
  const funcHash = crypto.createHash('sha1').update(funcBody).digest('base64');
  return `${funcHash}::${relativeLineNum}`;
}

main()
  .then(() => console.log("done"))
  .catch((e) => console.error(e));


// (if_statement 
//   condition: (not_operator argument: (identifier)) 
//   (comment) 
//   (comment) 
//   consequence: 
//     (block 
//       (expression_statement 
//         (assignment left: (identifier) right: (none))) 
//       (comment) 
//       (if_statement 
//         condition: 
//           (not_operator 
//             argument: (call function: (attribute object: (identifier) attribute: (identifier)) arguments: (argument_list))) 
//         consequence: 
//           (block 
//             (expression_statement 
//               (assignment 
//                 left: (identifier) 
//                 right: (call 
//                   function: (attribute object: (identifier) attribute: (identifier)) 
//                   arguments: (argument_list (keyword_argument name: (identifier) value: (attribute object: (identifier) attribute: (identifier))) 
//                   (keyword_argument 
//                     name: (identifier) 
//                     value: (attribute object: (identifier) attribute: (identifier))))))))) 
//       (comment) 
//       (comment) 
//       (expression_statement 
//         (assignment 
//           left: (identifier) 
//           right: (await 
//             (call 
//               function: (attribute object: (identifier) attribute: (identifier)) 
//               arguments: (argument_list 
//                 (keyword_argument name: (identifier) value: (identifier)) 
//                 (keyword_argument name: (identifier) value: 
//                   (conditional_expression 
//                     (attribute object: (attribute object: (identifier) attribute: (identifier)) attribute: (identifier)) 
//                     (attribute object: (identifier) attribute: (identifier)) 
//                     (none))) 
//                 (keyword_argument name: (identifier) value: (attribute object: (identifier) attribute: (identifier))) 
//                 (keyword_argument name: (identifier) value: (identifier)))))))) 
//   alternative: 
//     (elif_clause 
//       condition: (boolean_operator 
//         left: (attribute object: (identifier) attribute: (identifier)) 
//         right: (comparison_operator 
//           (attribute object: (identifier) attribute: (identifier)) 
//           (attribute object: (attribute object: (identifier) attribute: (identifier)) attribute: (identifier)))) 
//       consequence: 
//         (block 
//           (expression_statement 
//             (call 
//               function: (attribute object: (identifier) attribute: (identifier)) 
//               arguments: (argument_list 
//                 (string 
//                   (string_start) 
//                   (string_content) 
//                   (interpolation expression: (attribute object: (identifier) attribute: (identifier))) 
//                   (string_end)) 
//                 (attribute object: 
//                   (attribute object: (identifier) attribute: (identifier)) 
//                   attribute: (identifier))))) 
//           (expression_statement 
//             (call function: (attribute object: (identifier) attribute: (identifier)) arguments: (argument_list (keyword_argument name: (identifier) value: (attribute object: (identifier) attribute: (identifier))) (keyword_argument name: (identifier) value: (attribute object: (identifier) attribute: (identifier)))))) (raise_statement (call function: (identifier) arguments: (argument_list (string (string_start) (string_content) (string_end))))))))