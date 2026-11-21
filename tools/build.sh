#!/bin/sh
# Monta a pasta dist/ só com os arquivos públicos do site.
# Cloudflare Pages: build command "sh tools/build.sh", build output directory "dist".
set -eu

cd "$(dirname "$0")/.."

rm -rf dist
mkdir dist
cp -R index.html 404.html robots.txt sitemap.xml site.webmanifest assets dist/

for item in index.html 404.html robots.txt sitemap.xml site.webmanifest assets; do
  if [ ! -e "dist/$item" ]; then
    echo "erro: '$item' não foi copiado para dist/" >&2
    exit 1
  fi
done

echo "dist/ pronto com $(find dist -type f | wc -l | tr -d ' ') arquivos"
