import {
  GithubRepo,
  GithubRepoFeatureState,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import {
  CreateGithubRepoOperation,
  CreateGithubRepoRequestBody,
  CreateGithubRepoResponseBody,
  GetGithubReposOperation,
  GetGithubReposResponseBody,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import {
  GetGithubInstallationOperation,
  GetGithubInstallationResponseBody,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github.js";
import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import {
  TestContextBase,
  TestUtil,
} from "@eave-fyi/eave-stdlib-ts/src/test-util.js";
import { InstallationRepositoriesAddedEvent } from "@octokit/webhooks-types";
import anyTest, { TestFn } from "ava";
import sinon from "sinon";
import { maybeAddReposToDataBase } from "../src/events/installation-repositories-added.js";

interface TestContext extends TestContextBase {
  sandbox: sinon.SinonSandbox;
}

const test = anyTest as TestFn<TestContext>;

function anyTeam(t: TestUtil): Team {
  return {
    id: t.anystr(),
    name: t.anystr(),
    document_platform: null,
  };
}

function anyRepo(t: TestUtil): GithubRepo {
  return {
    id: t.anystr(),
    team_id: t.anystr(),
    external_repo_id: t.anystr(),
    display_name: null,
    github_installation_id: t.anystr(),
    inline_code_documentation_state: GithubRepoFeatureState.DISABLED,
    architecture_documentation_state: GithubRepoFeatureState.DISABLED,
    api_documentation_state: GithubRepoFeatureState.DISABLED,
  };
}

function anyGithubInstallationResponse(
  t: TestUtil,
): GetGithubInstallationResponseBody {
  const team_id = t.anystr();
  return {
    team: { id: team_id, name: t.anystr(), document_platform: null },
    github_integration: {
      id: t.anystr("github_installation_id"),
      github_install_id: t.anystr(),
      team_id,
    },
  };
}

test.beforeEach((t) => {
  const sandbox = sinon.createSandbox();
  const util = new TestUtil();

  t.context = {
    sandbox,
    u: util,
  };
});

test.afterEach.always((t) => {
  t.context.sandbox.restore();
});

test.serial(
  "no existing github_repos for team should not insert rows",
  async (t) => {
    // GIVEN there are no entries in github_repos db for this team
    const getGithubReposStub = t.context.sandbox
      .stub(GetGithubReposOperation, "perform")
      .returns(
        Promise.resolve({ repos: [] } satisfies GetGithubReposResponseBody),
      );
    const createGithubRepoStub = t.context.sandbox.stub(
      CreateGithubRepoOperation,
      "perform",
    );

    // WHEN the Eave gh app is given access to a new repo
    // Force-casting here to avoid having to pass in all the unused fields
    const event = <InstallationRepositoriesAddedEvent>{
      repositories_added: [
        {
          node_id: t.context.u.anystr("repo1 id"),
          name: t.context.u.anystr("repo1 name"),
        },
      ],
    };
    await maybeAddReposToDataBase({
      event,
      ctx: LogContext.wrap(),
      eaveTeam: anyTeam(t.context.u),
    });

    // THEN no action is taken (beyond checking for existing entries in the db)
    t.deepEqual(getGithubReposStub.callCount, 1);
    t.assert(createGithubRepoStub.notCalled);
  },
);

test.serial(
  "multiple repos added at once lead to multiple db row creations",
  async (t) => {
    // GIVEN this team has existing repos with all inline_code_docs feature states ENABLED
    const getGithubReposStub = t.context.sandbox
      .stub(GetGithubReposOperation, "perform")
      .returns(
        Promise.resolve({
          repos: [anyRepo(t.context.u)],
        } satisfies GetGithubReposResponseBody),
      );
    t.context.sandbox
      .stub(GetGithubInstallationOperation, "perform")
      .returns(Promise.resolve(anyGithubInstallationResponse(t.context.u)));

    const createGithubRepoStub = t.context.sandbox
      .stub(CreateGithubRepoOperation, "perform")
      .returns(
        Promise.resolve({
          repo: anyRepo(t.context.u),
        } satisfies CreateGithubRepoResponseBody),
      );

    const event: any = {
      repositories_added: [
        {
          node_id: t.context.u.anystr("repo1 id"),
          name: t.context.u.anystr("repo1 name"),
        },
        {
          node_id: t.context.u.anystr("repo2 id"),
          name: t.context.u.anystr("repo2 name"),
        },
      ],
      installation: {
        id: t.context.u.anystr(),
      },
    };

    // WHEN the Eave gh app is given access to multiple new repos
    await maybeAddReposToDataBase({
      event,
      ctx: LogContext.wrap(),
      eaveTeam: anyTeam(t.context.u),
    });

    // THEN the multiple db rows are created
    t.deepEqual(getGithubReposStub.callCount, 1);
    t.deepEqual(createGithubRepoStub.callCount, 2);
    t.assert(
      createGithubRepoStub.firstCall.calledWithMatch(
        sinon.match({
          input: {
            repo: {
              external_repo_id: t.context.u.getstr("repo1 id"),
              display_name: t.context.u.getstr("repo1 name"),
            },
          } satisfies CreateGithubRepoRequestBody,
        }),
      ),
    );
    t.assert(
      createGithubRepoStub.secondCall.calledWithMatch(
        sinon.match({
          input: {
            repo: {
              external_repo_id: t.context.u.getstr("repo2 id"),
              display_name: t.context.u.getstr("repo2 name"),
            },
          } satisfies CreateGithubRepoRequestBody,
        }),
      ),
    );
  },
);
