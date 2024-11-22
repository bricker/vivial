set -eu

./node_modules/.bin/graphql-codegen --config codegen.ts --overwrite --watch
