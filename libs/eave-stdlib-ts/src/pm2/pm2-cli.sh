#!/usr/bin/env sh

defaultconfigfile="./node_modules/@eave-fyi/eave-stdlib-ts/src/pm2/pm2-default-config.cjs"
configfile="${1:-$defaultconfigfile}"

./node_modules/.bin/pm2 \
  --no-daemon \
  --silent \
  --no-pmx \
  --no-automation \
  --disable-trace \
  --no-vizion \
  start "$configfile"