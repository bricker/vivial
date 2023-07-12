```mermaid
graph LR
    eavedevopsinfrastructure(Eave DevOps Infrastructure)
    eaveslackservice(Eave Slack Service)
    eavegithubservice(Eave Github Service)
    eaveconfluenceservice(Eave Confluence Service)
    eavejiraservice(Eave Jira Service)
    eavecoreservice(Eave Core Service)
    eavedevelopmenttools(Eave Development Tools)
    eavemarketingservice(Eave Marketing Service)
    eavearcherservice(Eave Archer Service)
    eavestandardlibrarypython(Eave Standard Library (Python))
    eavepubsubschemas(Eave PubSub Schemas)
    eavestandardlibrarytypescript(Eave Standard Library (TypeScript))

    eavedevopsinfrastructure-->eaveslackservice

    eavedevopsinfrastructure-->eavegithubservice

    eavedevopsinfrastructure-->eaveconfluenceservice

    eavedevopsinfrastructure-->eavejiraservice

    eavedevopsinfrastructure-->eavecoreservice
    eavedevopsinfrastructure-->eaveslackservice
    eavedevopsinfrastructure-->eavegithubservice
    eavedevopsinfrastructure-->eaveconfluenceservice
    eavedevopsinfrastructure-->eavejiraservice
    eavedevopsinfrastructure-->eavecoreservice
    eavedevopsinfrastructure-->eavedevopsinfrastructure
    eavedevelopmenttools-->eavegithubservice
    eavedevelopmenttools-->eavedevopsinfrastructure
    eavedevelopmenttools-->eavedevelopmenttools
    eavedevelopmenttools-->eaveslackservice
    eavedevelopmenttools-->eaveconfluenceservice
    eavedevelopmenttools-->eavejiraservice
    eavedevelopmenttools-->eavecoreservice

    eavedevelopmenttools-->eavemarketingservice

    eavedevelopmenttools-->eavearcherservice

    eavedevelopmenttools-->eavestandardlibrarypython
    eavedevopsinfrastructure-->eavedevelopmenttools
    eavedevopsinfrastructure-->eavemarketingservice
    eavedevopsinfrastructure-->eavearcherservice

    eavedevopsinfrastructure-->eavepubsubschemas

    eavedevopsinfrastructure-->eavestandardlibrarytypescript
    eavedevopsinfrastructure-->eavestandardlibrarypython
    eavedevopsinfrastructure-->eavedevopsinfrastructure
    eavedevopsinfrastructure-->eavedevelopmenttools
    eavedevopsinfrastructure-->eavemarketingservice
    eavedevopsinfrastructure-->eavearcherservice
    eavedevopsinfrastructure-->eavepubsubschemas
    eavedevopsinfrastructure-->eavestandardlibrarytypescript
    eavedevopsinfrastructure-->eavestandardlibrarypython
    eavedevelopmenttools-->eavegithubservice
    eavedevelopmenttools-->eavedevopsinfrastructure
    eavedevelopmenttools-->eavedevelopmenttools
    eavedevelopmenttools-->eaveslackservice
    eavedevelopmenttools-->eaveconfluenceservice
    eavedevelopmenttools-->eavejiraservice
    eavedevelopmenttools-->eavecoreservice
    eavedevelopmenttools-->eavemarketingservice
    eavedevelopmenttools-->eavearcherservice
    eavedevelopmenttools-->eavestandardlibrarypython
```

