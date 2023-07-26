I'm a technical writer who has been hired by a medium-sized tech company. It's my first day on the job, and my task is to create an overview of the company's system architecture. The expected output is a document with a brief summary of each system component, and an architecture diagram showing the flow of data and how the components are related to each other. A "system component" in this context is a discreet, shared API, probably accessed over HTTP.

Having worked at many companies, on many types of projects, many languages and frameworks, and many cloud service providers, I have a strong intuition for what is likely to be a system component that should be included in this architecture overview.

Here are the steps I'll take to accomplish this task:

1. Clone each active repository in the company's Github org (ignoring archived repositories)

1. Sort the repostitories by descending activity level (for example, last commit date or number of commits per time period). Activity level is a simple metric that roughly correlates with the importance of a repository.

1. For each repository, create a list of references to other system components. Because it's my first day on the job, I don't have a thorough understanding of what's relevant, so if there is some ambiguity I'll include the reference and investigate it later. To figure out the system components referenced in this repository:

  1. Find a list of explicit dependencies (requirements.txt, package.json, Gemfile, etc.) and note anything that is (or may be) an SDK/library for a system component.

  1. Read every source code file and note references to system components such as:
    - databases
    - cache
    - pub/sub
    - analytics
    - internal APIs
    - third-party APIs

1. Once I have a list of each repository's references to other components, go through the list again and investigate anything that I'm not sure about. Filter out anything that doesn't qualify for the system architecture overview.

  1. If it's something that seems internal to the organization, search GitHub for references to it.

  1. If it's something that seems like a third-party service, search the internet to learn about it. For package dependencies, look in the corresponding package index (npm, pypi, etc), or Google to learn about it.

1. Filter the list down to just the main system components.