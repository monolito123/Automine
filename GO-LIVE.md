# Go-live checklist — automine.com.br

One-time setup to publish the site at **https://automine.com.br** and forward **vendas@automine.com.br** to an existing inbox for free with ImprovMX. Do the steps in this order.

**Starting point** (checked against public DNS on 21 Nov 2026):

- **Domain:** registered at Registro.br, which also hosts its DNS (`a.auto.dns.br`, `b.auto.dns.br`).
- **Website records:** none yet.
- **E-mail:** turned off by Registro.br's defaults: a null MX (`0 .`), `v=spf1 -all` and DMARC `p=reject`. Mail sent to the domain bounces until step 3.

---

## 1. GitHub: turn on hosting (about 2 min)

Do this before touching DNS. GitHub recommends adding the custom domain in the repository first, so nobody else can claim it.

- [ ] **Settings → General → Default branch**: switch to `main`.
- [ ] **Settings → Pages → Build and deployment → Source**: choose **GitHub Actions**.
- [ ] **Settings → Pages → Custom domain**: type `automine.com.br` and **Save**. GitHub's DNS check will complain until step 3 is done. That's expected.
- [ ] **Actions → "Deploy site to GitHub Pages" → Run workflow** (or ask Claude to trigger it). The run should go green.

> If the run fails with *"Branch main is not allowed to deploy to github-pages due to environment protection rules"*, go to **Settings → Environments → github-pages → Deployment branches and tags** and add `main`.

## 2. ImprovMX: free e-mail forwarding (about 5 min)

- [ ] Create a free account at **improvmx.com** and add the domain `automine.com.br`.
- [ ] Create the alias **`vendas`** and point it at the inbox that should receive the leads (e.g. your Gmail).
- [ ] ImprovMX creates a catch-all alias (`*`) by default, which forwards *every* address `@automine.com.br`. Delete it if you only want `vendas@`; that means less spam.

> **Free plan** (ImprovMX pricing page): 1 domain, 25 aliases, 500 forwarded e-mails a day (past that, mail bounces until 00:00 UTC) and 7 days of logs. Sending through ImprovMX (SMTP) is paid only, so replies go out from your own inbox, not from `vendas@`.

## 3. Registro.br: DNS, all in one session

Go to **registro.br → Painel → automine.com.br → DNS → Editar zona**. In the **Name** field, "(empty)" means the domain itself. Type the other names without the domain suffix (e.g. `www`, `_dmarc`): Registro.br adds `.automine.com.br` for you.

### Remove: these block e-mail

| Type | Name   | Value |
|------|--------|-------|
| MX   | (empty) | `0 .` (null MX) |
| TXT  | (empty) | `v=spf1 -all` (replaced by ImprovMX's SPF below) |

### Keep

| Type | Name     | Value | Why |
|------|----------|-------|-----|
| TXT  | `_dmarc` | `v=DMARC1; p=reject;` | The domain never sends mail itself, so this stops anyone faking `vendas@automine.com.br`. It doesn't affect forwarded mail. |

### Add: website (GitHub Pages)

| Type  | Name   | Value                   |
|-------|--------|-------------------------|
| A     | (empty) | `185.199.108.153`       |
| A     | (empty) | `185.199.109.153`       |
| A     | (empty) | `185.199.110.153`       |
| A     | (empty) | `185.199.111.153`       |
| AAAA  | (empty) | `2606:50c0:8000::153`   |
| AAAA  | (empty) | `2606:50c0:8001::153`   |
| AAAA  | (empty) | `2606:50c0:8002::153`   |
| AAAA  | (empty) | `2606:50c0:8003::153`   |
| CNAME | `www`  | `monolito123.github.io` |

### Add: e-mail forwarding (ImprovMX)

| Type | Name   | Priority | Value |
|------|--------|----------|-------|
| MX   | (empty) | 10       | `mx1.improvmx.com` |
| MX   | (empty) | 20       | `mx2.improvmx.com` |
| TXT  | (empty) |          | `v=spf1 include:spf.improvmx.com ~all` |

Keep **only one** SPF record (`v=spf1 …`). ImprovMX needs it because forwarded mail goes out with your domain as the envelope sender, so it can handle bounces.

## 4. Finish and test

- [ ] **GitHub → Settings → Pages**: once the certificate is ready, tick **Enforce HTTPS**. This usually takes under an hour and can take up to 24 h.
- [ ] Open https://automine.com.br and https://www.automine.com.br. The second should redirect to the first.
- [ ] From an account **other than** the destination inbox, send an e-mail to `vendas@automine.com.br`. It should arrive within a minute or two. Gmail hides copies of messages you sent to yourself, so testing from the same account looks like a failure. ImprovMX's dashboard shows the domain status and delivery logs. ImprovMX says DNS changes can take 24–48 h to fully propagate, though Registro.br is usually much faster.
- [ ] Click the site's e-mail buttons and submit the contact form with "Enviar por e-mail". The message should reach your inbox.

### Optional

- [ ] Verify the domain on GitHub (**profile → Settings → Pages → Add a domain**). This adds one TXT record and prevents domain takeover.
- [ ] Add the site to Google Search Console and submit `https://automine.com.br/sitemap.xml`.
