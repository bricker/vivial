```mermaid
graph LR
    eaveslackservice(Eave Slack Service)
    eavecoreservice(Eave Core Service)
    eaveslackservice-->eaveslackservice

    eaveslackservice-->eavecoreservice
    eaveslackservice-->eaveslackservice
    eaveslackservice-->eavecoreservice
```