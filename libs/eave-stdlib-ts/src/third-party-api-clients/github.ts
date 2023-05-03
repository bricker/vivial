import { App, Octokit } from "octokit";
import { SuperAgent } from "superagent";
import { Pair } from "../types";
import { ApiClientBase } from "./base";


const GITHUB_APP_ID: string = "300560"

// Source response object defined in Github API
// https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
export type GithubRepository = {
  node_id: string;
  full_name: string;
}

// Source response object defined in Github API
// https://docs.github.com/en/rest/apps/apps?apiVersion=2022-11-28#create-an-installation-access-token-for-an-app
export type GithubInstallationAccessToken = {
  token: string;
  expires_at: string;
}

export class GithubClient implements ApiClientBase {
  accessToken: string | null = null;
  appId = GITHUB_APP_ID;
  installationId: string;
  private client: Octokit | null = null;
  private app: App;

  constructor(installationId: string) {
    this.installationId = installationId;
    // privateKey = eave_signing.get_key(eave_origins.ExternalOrigin.github_api_client.value) // ???
    this.app = new App({appId: this.appId, privateKey: 'TODO'}); // TODO
  }

  /**
   * Fetch content of the file located at the URL `url`.
   * @returns null on GitHub API request failure
   */
  async getFileContent(url: string): Promise<string | null> {
    try {
      return this.getRawContent(url);
    } catch (error) {
      // TODO: logger?
      console.log(error);
      return null;
    }
  }

  /**
   * Request data about the github repo pointed to by `url` from the GitHub API
   * (`url` doesnt have to point directly to the repo, it can point to any file w/in the repo too)
   */
  async getRepo(url: string): Promise<GithubRepository> {
    const client = await this.getClient();

    // gather data for API request URL
    const { first: owner, second: repo} = this.getRepoLocation(url);

    // https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
    const { data: repository } = await client.rest.repos.get({owner, repo});
    return <GithubRepository>repository;
  }

  /**
   * Parse the GitHub org name and repo name from the input `url`
   * @returns Pair(org name, repo name)
   */
  private getRepoLocation(url: string): Pair<string, string> {
    // split path from URL
    const urlPathComponents = (new URL(url)).pathname.split('/');

    if (urlPathComponents.length < 3) {
      throw Error(`GitHub URL ${url} did not contain expected org and repo name in its path`);
    }

    // urlPathComponents === ['', 'org', 'repo', ...]
    return { first: urlPathComponents[1]!, second: urlPathComponents[2]! }
  }

  /**
   * Fetch github file content from `url` using the raw.githubusercontent.com feature
   * Returns null if `url` is not a path to a file (or if some other error was encountered).
   * 
   * NOTE: raw.githubusercontent.com is ratelimitted by IP, not requesting user, so this wont scale far
   * https://github.com/github/docs/issues/8031#issuecomment-881427112
   */
  private async getRawContent(url: string): Promise<string | null> {
    const urlComponents = new URL(url);
    // remove blob from URL since raw content URLs dont have it
    const contentLocation = urlComponents.pathname.replace('blob/', '');
    let rawUrl = '';
    // check if enterprise host
    if (!(urlComponents.hostname.match(/github\.com/))) {
      rawUrl = `https://${urlComponents.hostname}/raw`;
    } else {
      rawUrl = 'https://raw.githubusercontent.com';
    }

    const requestUrl = `${rawUrl}${contentLocation}`;

    // get auth token if haven't already
    await this.setInstallationToken(this.appId, this.installationId, url);

    const headers = {
                  "Authorization": `Bearer ${this.accessToken}`,
            "Accept": "application/vnd.github.v3.raw",
    }

    //         async with aiohttp.ClientSession() as http_session:
//             resp = await http_session.request(
//                 method="GET",
//                 url=request_url,
//                 headers=headers,
//             )
//             file_content = await resp.text()

//             # gh returns 404 text if no raw content at URL path
//             if file_content == "404: Not Found":
//                 return None
//             return file_content
  }

  /**
   * Get or build a octokit client prepared with the necessary authentication
   * for with the GitHub API of the passed in URL.
   * If a new octokit is built, it is locally cached for later use.
   */
  private async getClient(): Promise<Octokit> {
    if (this.client === null) {
      this.client = await this.createClient();
    }

    return this.client!;
  }

  private async createClient(): Promise<Octokit> {
    const octokit = await this.app.getInstallationOctokit(parseInt(this.installationId, 10));
    return octokit;
  }

  /**
   * Create an installation token for the app identified by `appId`
   * that can authenticate with the GitHub API required to access the
   * resource at `url`.
   * The created installation token is then set in `this.accessToken`.
   * 
   * @param appId -- ID of the GitHub App to authenticate through
   * @param installationId -- ID of the installation to authenticate as
   * @param url -- resource the installation token should be able to access
   * @returns the created access token after saving it in `this.accessToken`
   */
  private async setInstallationToken(appId: string, installationId: string, url: string): Promise<string> {
    // TODO: only need this for raw content?? even worth?
  }
}

//     async def _set_installation_token(self, app_id: str, installation_id: str, url: str) -> str:
//         """

//         """
//         if self.access_token:
//             # token has already been set
//             return self.access_token

//         # temporarily set auth token as JWT so we can auth as app
//         jwt_token = self._create_jwt(app_id)
//         # request installation access token.
//         # create 1-time-use client with JWT auth
//         client = self._create_session(domain=urlparse(url).netloc, token=jwt_token)

//         async with client.post(f"/app/installations/{installation_id}/access_tokens") as token_resp:
//             token_json: dict[str, Any] = await token_resp.json()
//             token_data = GithubInstallationAccessToken.from_response(token_json)
//             self.access_token = token_data.token

//         await client.close()
//         return self.access_token
