```mermaid
graph LR
  subgraph Eave
  github_server
  end
  github_server-->eave

  github_server-->openai

  github_server-->github

  subgraph Eave
  github_server
  end
  github_server-->eave

  github_server-->openai

  github_server-->github

  subgraph Eave
  jira_server
  end
  jira_server-->openai

  jira_server-->eave

  jira_server-->google_app_engine

  jira_server-->jira

  jira_server-->atlassian

  subgraph Eave
  confluence_server
  end
  confluence_server-->openai

  confluence_server-->atlassian

  confluence_server-->confluence

  subgraph Eave
  confluence_server
  end
  confluence_server-->openai

  confluence_server-->atlassian

  confluence_server-->confluence


```
