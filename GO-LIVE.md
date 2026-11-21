# Go-live checklist — automine.com.br

- **Website:** the Cloudflare Worker `automine`, published with `tools/deploy_cloudflare.py` (see the README). It's live now at https://automine.automine40.workers.dev. `automine.com.br` and `www.automine.com.br` are already attached to it.
- **E-mail:** Cloudflare Email Routing forwards `vendas@automine.com.br` to `automine40@gmail.com`. The destination is verified and the rule is enabled.
- **What still blocks both:** the domain still uses Registro.br's nameservers, so the Cloudflare zone is **pending**. Step 1 fixes that.

## Status (21 Nov 2026, 22:50 UTC)

| Item | Status |
|---|---|
| Site published on Cloudflare (workers.dev) | Done |
| `automine.com.br` and `www` attached to the Worker | Done. They go live when the zone is Active |
| Old DNSSEC DS record removed at Registro.br | Done (22:12 UTC) |
| Imported records that blocked e-mail (null MX, `v=spf1 -all`) | Removed from the Cloudflare zone |
| Gmail destination verified, `vendas@` forwarding rule | Done |
| Nameservers at Registro.br switched to Cloudflare | **To do** (step 1) |
| Email Routing turned on (MX, SPF, DKIM) | After the zone is Active (step 2) |

## 1. Registro.br: switch the nameservers (after 21:00 Brasília time on 21 Nov)

Resolvers can keep the old DS cached for up to one hour after its removal at 22:12 UTC (the `.com.br` DS TTL is 3600 s). Waiting until 21:00 Brasília time (00:00 UTC) leaves a margin.

- [ ] **Registro.br → automine.com.br → DNS servers:** replace `a.auto.dns.br` and `b.auto.dns.br` with:
  - `lewis.ns.cloudflare.com`
  - `samara.ns.cloudflare.com`
- [ ] Wait until Cloudflare marks the zone **Active** (usually under an hour).

## 2. Turn on Email Routing (after Active)

- [ ] **Cloudflare → automine.com.br → Email → Email Routing:** enable it, or ask Claude (it's one API call). Cloudflare adds MX `route1/2/3.mx.cloudflare.net` (priorities 5, 78, 88), TXT `v=spf1 include:_spf.mx.cloudflare.net ~all` and the DKIM TXT `cf2024-1._domainkey`.
- The `vendas@` → `automine40@gmail.com` rule already exists. Cloudflare doesn't allow turning Email Routing on before the zone is active.

## 3. Test

- [ ] `https://automine.com.br` opens. `https://www.automine.com.br` redirects to it.
- [ ] From an account other than `automine40@gmail.com`, send to `vendas@automine.com.br`. It should arrive within a minute or two. Gmail hides copies of messages you sent yourself, so a self-test looks like a failure.
- [ ] The site's e-mail buttons and the contact form ("Enviar por e-mail") open the e-mail with the message ready.

## 4. Optional

- [ ] **DNSSEC:** Cloudflare → automine.com.br → DNSSEC → Enable, then add the DS it shows at Registro.br. Ask Claude to verify it afterwards, because a wrong DS takes the domain down for validating resolvers.
- [ ] **Send as `vendas@` from Gmail.** Email Routing only receives. To send, Gmail's "Send mail as" needs an SMTP server for the domain:
  - **Cloudflare Email Sending:** needs the paid Workers plan and is in beta (3,000 e-mails a month included). Onboard the domain under **Email Service → Email Sending**. Create an API token with **Email Sending: Edit**. Then, in Gmail, set SMTP server `smtp.mx.cloudflare.net`, port 465, SSL, username `api_token`, and the token as the password.
  - **A free SMTP provider** (for example Brevo; check its current limits). Add the DNS records its dashboard shows. If it needs an SPF `include:`, add it to the same single SPF record.
- [ ] **Automatic deploys on every push:** connect this repository in Cloudflare (Workers & Pages → Create → Import a repository). Until then, run `tools/deploy_cloudflare.py` after changing the site.
- [ ] Add the site to Google Search Console and submit `https://automine.com.br/sitemap.xml`.
