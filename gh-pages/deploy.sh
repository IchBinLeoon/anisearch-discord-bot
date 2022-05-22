#!/usr/bin/env sh

set -e

npm run build

cd dist

git init
git add -A
git commit -m 'Deploy'

git push -f https://github.com/IchBinLeoon/anisearch-discord-bot.git main:gh-pages

cd -