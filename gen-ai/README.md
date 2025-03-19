# Generative AI templates

This folder contains templates that require an LLM to run, and therefore, require special credentials to run/host.

Since credentials are required, the hosted versions of these apps are being deployed through [this Connect Cloud account](https://connect.posit.cloud/posit-ai), which is also managing the credentials.

Note that you can use `shiny create` to obtain a copy of each Gen AI template with a command that looks like this:

```shell
shiny create --template workout-plan --github posit-dev/py-shiny-templates/gen-ai
```
