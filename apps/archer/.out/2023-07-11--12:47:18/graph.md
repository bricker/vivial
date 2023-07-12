```mermaid
graph LR
    eaveslackintegration(Eave Slack Integration)
    eavedevopsinfrastructure(Eave DevOps Infrastructure)
    eavestandardlibrarypython(Eave Standard Library (Python))
    eavepubsubschemas(Eave PubSub Schemas)
    eavecoreservice(Eave Core Service)
    openaiservice(OpenAI Service)

    eaveslackintegration-->eavedevopsinfrastructure

    eaveslackintegration-->eavestandardlibrarypython

    eaveslackintegration-->eavepubsubschemas
    eaveslackintegration-->eavedevopsinfrastructure
    eaveslackintegration-->eavestandardlibrarypython
    eaveslackintegration-->eavepubsubschemas
    eaveslackintegration-->eaveslackintegration

    eaveslackintegration-->eavecoreservice

    eaveslackintegration-->openaiservice
    eaveslackintegration-->eaveslackintegration
    eaveslackintegration-->eavecoreservice
    eaveslackintegration-->openaiservice
```