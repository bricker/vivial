```mermaid
graph LR
    eavedevops(Eave DevOps)
    eaveslack(Eave Slack)
    eavegithub(Eave Github)
    eaveconfluence(Eave Confluence)
    eavejira(Eave Jira)
    hashicorpgoogle(hashicorp/google)
    eavecore(Eave Core)

    eavedevops-->eaveslack

    eavedevops-->eavegithub

    eavedevops-->eaveconfluence

    eavedevops-->eavejira

    eavedevops-->hashicorpgoogle
```

