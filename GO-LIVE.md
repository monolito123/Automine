# Go-live checklist — automine.com.br

The site is live at **https://automine.com.br** (Cloudflare Worker `automine`, published with `tools/deploy_cloudflare.py`). E-mail for the domain is forwarded by Cloudflare Email Routing.

## Status (22 Nov 2026)

| Item | Status |
|---|---|
| Nameservers at Registro.br → `lewis.ns.cloudflare.com`, `samara.ns.cloudflare.com` | Done. The zone is active |
| Site on `automine.com.br`. `www` and `http://` redirect to `https://automine.com.br` | Done |
| Cloudflare zone settings: Always Use HTTPS on, minimum TLS 1.2 | Done |
| Email Routing on (MX `route1/2/3.mx.cloudflare.net`, SPF, DKIM `cf2024-1`) | Done |
| `vendas@`, `felipe@`, `rafael@` and `lucas@automine.com.br` → `automine40@gmail.com` | Done (destination verified) |
| Lighthouse (mobile and desktop) | 100 in performance, accessibility, best practices and SEO |

## Test once

- [ ] From an account **other than** `automine40@gmail.com`, send a message to each address. It should arrive within a minute or two. Gmail hides copies of messages you sent yourself, so a self-test looks like a failure.
- [ ] Open the site on a phone and tap the WhatsApp buttons. They open a chat with +55 (11) 91146-8446.

## Optional

- [ ] **DNSSEC:** Cloudflare → automine.com.br → DNSSEC → Enable, then add the DS it shows at Registro.br. Ask Claude to verify it afterwards, because a wrong DS takes the domain down for validating resolvers.
- [ ] **Send as these addresses from Gmail.** Email Routing only receives, so replies currently go out from `automine40@gmail.com`. To send as `vendas@` and the others, Gmail's "Send mail as" needs an SMTP server for the domain:
  - **Cloudflare Email Sending:** needs the paid Workers plan and is in beta (3,000 e-mails a month included). Onboard the domain under **Email Service → Email Sending**. Create an API token with **Email Sending: Edit**. Then, in Gmail, set SMTP server `smtp.mx.cloudflare.net`, port 465, SSL, username `api_token`, and the token as the password.
  - **A free SMTP provider** (for example Brevo; check its current limits). Add the DNS records its dashboard shows. If it needs an SPF `include:`, add it to the same single SPF record.
- [ ] **Tighten DMARC:** `_dmarc` is `v=DMARC1; p=reject;`. That's right while the domain doesn't send mail. If you set up sending, check that SPF and DKIM pass first.
- [ ] **Automatic deploys on every push:** connect this repository in Cloudflare (Workers & Pages → Create → Import a repository). Until then, run `tools/deploy_cloudflare.py` after changing the site.
- [ ] Add the site to Google Search Console and submit `https://automine.com.br/sitemap.xml`.
