```mermaid
graph LR
    eavedevopsinfrastructure(Eave DevOps Infrastructure)
    eaveslackservice(Eave Slack Service)
    eavegithubservice(Eave Github Service)
    eaveconfluenceservice(Eave Confluence Service)
    eavejiraservice(Eave Jira Service)
    eavedevelopmenttools(Eave Development Tools)
    googlecloudkms(Google Cloud KMS)
    python(Python)
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

    eavedevelopmenttools-->googlecloudkms
    eavedevelopmenttools-->eavegithubservice
    eavedevelopmenttools-->googlecloudkms
    eavedevelopmenttools-->eavegithubservice
    eavedevelopmenttools-->eavedevelopmenttools
    eavedevelopmenttools-->eaveslackservice
    eavedevelopmenttools-->eaveconfluenceservice
    eavedevelopmenttools-->eavejiraservice
    eavedevelopmenttools-->eavedevopsinfrastructure

    eavedevelopmenttools-->python

    eavedevelopmenttools-->eavecoreservice

    eavedevelopmenttools-->eavemarketingservice

    eavedevelopmenttools-->eavearcherservice

    eavedevelopmenttools-->eavestandardlibrarypython
    eavedevelopmenttools-->eavedevelopmenttools
    eavedevelopmenttools-->eaveslackservice
    eavedevelopmenttools-->eaveconfluenceservice
    eavedevelopmenttools-->eavejiraservice
    eavedevelopmenttools-->eavedevopsinfrastructure
    eavedevelopmenttools-->python
    eavedevelopmenttools-->eavecoreservice
    eavedevelopmenttools-->eavemarketingservice
    eavedevelopmenttools-->eavearcherservice
    eavedevelopmenttools-->eavestandardlibrarypython
```

