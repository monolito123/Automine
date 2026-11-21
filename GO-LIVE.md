# Go-live checklist — automine.com.br

One-time setup to publish the site at **https://automine.com.br** and create **vendas@automine.com.br** on Zoho Mail. Do the steps in this order.

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

## 2. Zoho Mail: create the account and mailbox (about 10 min)

- [ ] Sign up at **zoho.com/mail** (business e-mail) and pick a plan. Zoho lists a **Mail Free** plan (up to 5 users, 5 GB each, web and mobile app only, no IMAP/POP) but says it's "available only in select data centers". If it isn't offered to you, **Mail Lite** is the low-cost paid option. Prices are shown in BRL.
- [ ] When asked for a domain, enter `automine.com.br`.
- [ ] Create the mailbox **vendas@automine.com.br**. The simplest setup is to make it the first (admin) account. If several people need it later, add them as users and turn `vendas@` into a group mailbox.
- [ ] Zoho shows a **verification TXT** value (`zoho-verification=zb…`). Keep that tab open: you add it in step 3, then click **Verify** in Zoho.
- [ ] After step 3: **Zoho Admin Console → Domains → automine.com.br → Email Configuration → DKIM → Add**. Use selector `zoho` and key length **1024**: the value then fits in a single TXT string, which is safest with Registro.br's editor. Copy the TXT value, add it in Registro.br (step 3, row DKIM), then click **Verify** and **Enable** in Zoho.

> **Data center:** these values are for Zoho's default `.com` data center. If your Zoho admin address ends in `.eu`, `.in` or `.com.au`, use the MX and SPF values Zoho shows you instead.

## 3. Registro.br: DNS, all in one session

Go to **registro.br → Painel → automine.com.br → DNS → Editar zona**. In the **Name** field, "(empty)" means the domain itself. Type the other names without the domain suffix (e.g. `www`, `_dmarc`): Registro.br adds `.automine.com.br` for you.

### Remove: these block e-mail

| Type | Name   | Value                  |
|------|--------|------------------------|
| MX   | (empty) | `0 .` (null MX)        |
| TXT  | (empty) | `v=spf1 -all`          |
| TXT  | `_dmarc` | `v=DMARC1; p=reject;` (replaced below) |

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

### Add: e-mail (Zoho Mail)

| Type | Name               | Priority | Value |
|------|--------------------|----------|-------|
| MX   | (empty)            | 10       | `mx.zoho.com` |
| MX   | (empty)            | 20       | `mx2.zoho.com` |
| MX   | (empty)            | 50       | `mx3.zoho.com` |
| TXT  | (empty)            |          | `v=spf1 include:zohomail.com ~all` |
| TXT  | (empty)            |          | `zoho-verification=zb…` (the exact value from Zoho, step 2) |
| TXT  | `zoho._domainkey`  |          | `v=DKIM1; k=rsa; p=…` (the exact value from Zoho, step 2) |
| TXT  | `_dmarc`           |          | `v=DMARC1; p=none;` (tightened in step 4) |

Keep **only one** SPF record (`v=spf1 …`). If you later send through another tool (CRM, newsletter), add its `include:` to that same record.

## 4. Finish and test

DNS changes at Registro.br usually show up within minutes. Allow up to a couple of hours.

- [ ] **GitHub → Settings → Pages**: once the certificate is ready, tick **Enforce HTTPS**. This usually takes under an hour and can take up to 24 h.
- [ ] Open https://automine.com.br and https://www.automine.com.br. The second should redirect to the first.
- [ ] Send a test from `vendas@automine.com.br` to a Gmail account, open it, and choose **⋮ → Show original**. SPF, DKIM and DMARC should all say **PASS**. Then reply to it to test incoming mail.
- [ ] Click the site's e-mail buttons and submit the contact form with "Enviar por e-mail". The message should reach the Zoho inbox.
- [ ] About a week later, if everything delivers fine, change `_dmarc` to `v=DMARC1; p=quarantine;`.

### Optional

- [ ] Verify the domain on GitHub (**profile → Settings → Pages → Add a domain**). This adds one TXT record and prevents domain takeover.
- [ ] Add the site to Google Search Console and submit `https://automine.com.br/sitemap.xml`.
