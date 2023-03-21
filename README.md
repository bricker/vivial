## Setup

### EAVE_HOME

First of all, set an environment variable called `EAVE_HOME` pointing to the root of this repository. This environment variable is used when an absolute file path is needed.

#### Bash or Zsh

```bash
# To set a variable on each login, add this to your login script, eg `~/.bashrc` or `~/.zshrc`
export EAVE_HOME=$HOME/code/eave-monorepo
```

#### Fish

```fish
# To set a global variable on each login (recommended), add this to a fish config file, eg $XDG_CONFIG_HOME/fish/config.fish
set -gx EAVE_HOME $HOME/code/eave-monorepo

# Or, to set a universal variable, run this interactively:
set -Ux EAVE_HOME $HOME/code/eave-monorepo
```

### IDE

For the fastest setup, built-in configuration, debug scripts, and more, it is recommended to use VSCode for development in this repository.

To get started, open `.vscode/eave.code-workspace` in VSCode.

### App Setup

Generally, each app has a setup script at `bin/setup`. From the root of the app (for example, `apps/core/`), run `bin/setup`. If something doesn't work or a step is missing, please update/fix it once you resolve the issue.

