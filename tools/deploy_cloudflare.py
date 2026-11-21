#!/usr/bin/env python3
"""Publica o site na Cloudflare como um Worker que serve os arquivos de dist/.

Uso:
    CLOUDFLARE_API_TOKEN=... python3 tools/deploy_cloudflare.py [--domains]

- Roda tools/build.sh e envia os arquivos públicos (dist/) como módulos de dados
  do Worker (sem etapa separada de upload de assets).
- Ativa o endereço <nome>.<subdomínio>.workers.dev.
- Com --domains, liga automine.com.br e www.automine.com.br ao Worker
  (a zona precisa estar "active" na Cloudflare).

Token: precisa de Workers Scripts: Edit (conta). Para --domains, também de
Workers Routes: Edit e Zone: Read (zona). CLOUDFLARE_ACCOUNT_ID é opcional.
"""
from __future__ import annotations

import json
import mimetypes
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
API = "https://api.cloudflare.com/client/v4"
WORKER_NAME = "automine"
ZONE_NAME = "automine.com.br"
HOSTNAMES = ["automine.com.br", "www.automine.com.br"]
COMPATIBILITY_DATE = "2026-11-01"

TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".woff2": "font/woff2",
    ".txt": "text/plain; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".webmanifest": "application/manifest+json; charset=utf-8",
}

WORKER_TEMPLATE = """\
{imports}

const FILES = {{
{entries}
}};

const SECURITY_HEADERS = {{
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
}};

export default {{
  async fetch(request) {{
    const url = new URL(request.url);
    if (url.hostname === "www.{zone}") {{
      url.hostname = "{zone}";
      return Response.redirect(url.toString(), 301);
    }}
    if (request.method !== "GET" && request.method !== "HEAD") {{
      return new Response("Method Not Allowed", {{ status: 405, headers: {{ allow: "GET, HEAD" }} }});
    }}
    let path = url.pathname;
    try {{
      path = decodeURIComponent(path);
    }} catch {{
      path = "/404.html";
    }}
    if (path.endsWith("/")) path += "index.html";
    let file = FILES[path];
    let status = 200;
    if (!file) {{
      file = FILES["/404.html"];
      status = 404;
    }}
    const headers = {{ "content-type": file.type, "cache-control": file.cache, ...SECURITY_HEADERS }};
    const body = request.method === "HEAD" ? null : file.body.slice(0);
    return new Response(body, {{ status, headers }});
  }},
}};
"""


def api(method: str, path: str, body: bytes | None = None, content_type: str = "application/json"):
    headers = {"Content-Type": content_type}
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(API + path, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.load(e)
        except Exception:
            return e.code, {"errors": [{"message": e.reason}]}


def errors(payload) -> str:
    errs = payload.get("errors") or []
    return "; ".join(f"{e.get('code')}: {e.get('message')}" for e in errs) or "ok"


def build_worker(files: list[pathlib.Path]) -> str:
    imports, entries = [], []
    for i, f in enumerate(files):
        rel = f.relative_to(DIST).as_posix()
        ctype = TYPES.get(f.suffix, mimetypes.guess_type(f.name)[0] or "application/octet-stream")
        cache = "public, max-age=0, must-revalidate" if f.suffix == ".html" else "public, max-age=86400"
        imports.append(f'import f{i} from "./{rel}";')
        entries.append(f'  "/{rel}": {{ body: f{i}, type: "{ctype}", cache: "{cache}" }},')
    return WORKER_TEMPLATE.format(imports="\n".join(imports), entries="\n".join(entries), zone=ZONE_NAME)


def multipart(parts: list[tuple[str, str, bytes]]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    out = bytearray()
    for name, ctype, data in parts:
        out += f"--{boundary}\r\n".encode()
        out += f'Content-Disposition: form-data; name="{name}"; filename="{name}"\r\n'.encode()
        out += f"Content-Type: {ctype}\r\n\r\n".encode()
        out += data + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


def main() -> int:
    subprocess.run(["sh", str(ROOT / "tools" / "build.sh")], check=True)
    files = sorted(p for p in DIST.rglob("*") if p.is_file())

    st, zones = api("GET", f"/zones?name={ZONE_NAME}")
    if st != 200 or not zones.get("result"):
        print(f"zona {ZONE_NAME} não encontrada: {errors(zones)}")
        return 1
    zone = zones["result"][0]
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or zone["account"]["id"]

    worker_js = build_worker(files).encode()
    metadata = json.dumps({"main_module": "worker.js", "compatibility_date": COMPATIBILITY_DATE}).encode()
    parts = [("metadata", "application/json", metadata), ("worker.js", "application/javascript+module", worker_js)]
    parts += [(f.relative_to(DIST).as_posix(), "application/octet-stream", f.read_bytes()) for f in files]
    body, ctype = multipart(parts)
    st, res = api("PUT", f"/accounts/{account_id}/workers/scripts/{WORKER_NAME}", body, ctype)
    print(f"upload do Worker ({len(files)} arquivos, {len(body) // 1024} KB): HTTP {st} {errors(res)}")
    if st != 200:
        return 1

    st, res = api("POST", f"/accounts/{account_id}/workers/scripts/{WORKER_NAME}/subdomain",
                  json.dumps({"enabled": True, "previews_enabled": False}).encode())
    st_sub, sub = api("GET", f"/accounts/{account_id}/workers/subdomain")
    name = (sub.get("result") or {}).get("subdomain")
    print(f"workers.dev: HTTP {st} {errors(res)} -> https://{WORKER_NAME}.{name}.workers.dev")

    if "--domains" in sys.argv:
        print(f"zona {ZONE_NAME}: {zone['status']}")
        for host in HOSTNAMES:
            payload = {"environment": "production", "hostname": host, "service": WORKER_NAME, "zone_id": zone["id"]}
            st, res = api("PUT", f"/accounts/{account_id}/workers/domains", json.dumps(payload).encode())
            print(f"domínio {host}: HTTP {st} {errors(res)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
