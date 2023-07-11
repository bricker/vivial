```mermaid
graph LR
    eaveslackservice(Eave Slack Service)
    eavecoreservice(Eave Core Service)
    eaveconfluenceservice(Eave Confluence Service)
    eaveslackservice-->eaveslackservice

    eaveslackservice-->eavecoreservice

    eaveslackservice-->eaveconfluenceservice
    eaveslackservice-->eaveslackservice
    eaveslackservice-->eavecoreservice
    eaveslackservice-->eaveconfluenceservice
```