```mermaid
graph LR
    eavedevopsinfrastructure(Eave DevOps Infrastructure)
    eaveslackservice(Eave Slack Service)
    eavegithubservice(Eave Github Service)
    eaveconfluenceservice(Eave Confluence Service)
    eavejiraservice(Eave Jira Service)
    eavedevelopmenttools(Eave Development Tools)
    gcriogooglecomcloudsdktoolcloudsdk(gcr.io/google.com/cloudsdktool/cloud-sdk)
    eavecoreservice(Eave Core Service)
    eavemarketingservice(Eave Marketing Service)
    eavearcherservice(Eave Archer Service)
    eavestandardlibrarypython(Eave Standard Library (Python))

    eavedevopsinfrastructure-->eaveslackservice

    eavedevopsinfrastructure-->eavegithubservice

    eavedevopsinfrastructure-->eaveconfluenceservice

    eavedevopsinfrastructure-->eavejiraservice
    eavedevopsinfrastructure-->eaveslackservice
    eavedevopsinfrastructure-->eavegithubservice
    eavedevopsinfrastructure-->eaveconfluenceservice
    eavedevopsinfrastructure-->eavejiraservice
    eavedevopsinfrastructure-->eavedevopsinfrastructure
    eavedevopsinfrastructure-->eavedevopsinfrastructure
    eavedevelopmenttools-->eavegithubservice
    eavedevelopmenttools-->eavegithubservice
    eavedevelopmenttools-->eavedevelopmenttools
    eavedevelopmenttools-->eavedevopsinfrastructure
    eavedevelopmenttools-->eaveslackservice
    eavedevelopmenttools-->eaveconfluenceservice
    eavedevelopmenttools-->eavejiraservice

    eavedevelopmenttools-->gcriogooglecomcloudsdktoolcloudsdk

    eavedevelopmenttools-->eavecoreservice

    eavedevelopmenttools-->eavemarketingservice

    eavedevelopmenttools-->eavearcherservice

    eavedevelopmenttools-->eavestandardlibrarypython
    eavedevelopmenttools-->eavedevelopmenttools
    eavedevelopmenttools-->eavedevopsinfrastructure
    eavedevelopmenttools-->eaveslackservice
    eavedevelopmenttools-->eaveconfluenceservice
    eavedevelopmenttools-->eavejiraservice
    eavedevelopmenttools-->gcriogooglecomcloudsdktoolcloudsdk
    eavedevelopmenttools-->eavecoreservice
    eavedevelopmenttools-->eavemarketingservice
    eavedevelopmenttools-->eavearcherservice
    eavedevelopmenttools-->eavestandardlibrarypython
```

