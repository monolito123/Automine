#!/bin/sh
# Monta a pasta dist/ só com os arquivos públicos do site e prepara para produção:
# - versiona os endereços de fontes, CSS, JS e ícones (?v=<hash>) para permitir cache longo;
# - embute o CSS no index.html (remove uma requisição que bloqueava a renderização).
# Usado por tools/deploy_cloudflare.py. Requer GNU sed e sha256sum (Linux).
set -eu

cd "$(dirname "$0")/.."

rm -rf dist
mkdir dist
cp -R index.html 404.html robots.txt sitemap.xml site.webmanifest assets dist/

version() { sha256sum "$1" | cut -c1-10; }

# 1) Fontes: mesma URL versionada no @font-face e no <link rel="preload">.
for font in dist/assets/fonts/*.woff2; do
  name=$(basename "$font")
  v=$(version "$font")
  sed -i "s|fonts/$name\"|fonts/$name?v=$v\"|g" dist/assets/css/styles.css dist/index.html dist/404.html
done

# 2) CSS embutido no index.html (caminhos das fontes passam a ser relativos à raiz).
inline=$(mktemp)
{
  printf '<style>\n'
  sed 's|url("\.\./fonts/|url("assets/fonts/|g' dist/assets/css/styles.css
  printf '</style>\n'
} > "$inline"
sed -i -e '/<link rel="stylesheet" href="assets\/css\/styles.css">/{r '"$inline" -e 'd}' dist/index.html
rm -f "$inline"

# 3) Demais arquivos referenciados pelas páginas.
for path in assets/css/styles.css assets/js/main.js assets/img/favicon.svg assets/img/apple-touch-icon.png; do
  v=$(version "dist/$path")
  sed -i "s|$path\"|$path?v=$v\"|g" dist/index.html dist/404.html
done

for item in index.html 404.html robots.txt sitemap.xml site.webmanifest assets; do
  if [ ! -e "dist/$item" ]; then
    echo "erro: '$item' não foi copiado para dist/" >&2
    exit 1
  fi
done
if grep -q '<link rel="stylesheet"' dist/index.html || ! grep -q 'main.js?v=' dist/index.html; then
  echo "erro: o CSS não foi embutido ou o JS não foi versionado no index.html" >&2
  exit 1
fi

echo "dist/ pronto com $(find dist -type f | wc -l | tr -d ' ') arquivos"
