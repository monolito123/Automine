# Go-live checklist — automine.com.br

- **Website:** built and hosted by **Cloudflare Pages** from the `main` branch of this repository, served at **https://automine.com.br**.
- **E-mail:** `vendas@automine.com.br` *receives* through Cloudflare Email Routing (free). It *sends* from Gmail's "Send mail as" through one of the options in step 6.

Do the steps in order. Steps 1 and 2 don't change the live domain. Step 3 changes DNS and needs a 24–48 h wait.

**Starting point** (checked against public DNS on 21 Nov 2026):

- **DNS:** Registro.br (`a.auto.dns.br`, `b.auto.dns.br`).
- **DNSSEC:** on. DS record at the `.br` registry with key tag `33150`, algorithm 13.
- **Website records:** none.
- **E-mail:** off, because of Registro.br's defaults: null MX `0 .`, `v=spf1 -all` and DMARC `p=reject`.

---

## 1. Cloudflare Pages: build and test on pages.dev (about 10 min)

No DNS changes are needed for this step.

- [ ] **Workers & Pages → Create application → Pages → Connect to Git.** Choose GitHub and authorize the Cloudflare GitHub app for `monolito123/Automine`.
- [ ] **Project name:** `automine` (this creates `automine.pages.dev`). If the name is taken, choose another.
- [ ] **Production branch:** `main`.
- [ ] **Build command:** `sh tools/build.sh`. **Build output directory:** `dist`. **Root directory:** leave empty.
- [ ] **Save and Deploy.** Open `https://automine.pages.dev` and check the page. Open `/naoexiste` too; it should show the 404 page.

## 2. Cloudflare: add the domain on the Free plan (about 15 min)

- [ ] **Domains → Onboard a domain** → `automine.com.br` → **Full setup** → **Free** plan. Cloudflare copies the current records.
- [ ] **Delete** MX `@` (`0 .`) and TXT `@` (`v=spf1 -all`).
- [ ] **Edit** TXT `_dmarc` to `v=DMARC1; p=none;`. Tighten it in step 8.
- [ ] **Don't add website records** (A, AAAA, or a `www` CNAME pointing to GitHub). Step 4 creates the right ones. If you added GitHub records earlier, delete them, because they conflict with the Pages domain.
- [ ] Note the **two nameservers** Cloudflare assigns (`xxxx.ns.cloudflare.com`).

## 3. Registro.br: remove DNSSEC, wait, then change nameservers (day 1, then day 2–3)

The order matters. If the old DS record stays while the nameservers change, DNSSEC-validating resolvers will reject the domain.

- [ ] **Registro.br → Painel → automine.com.br → DNSSEC:** remove the DS record with key tag `33150`. Save. If the panel doesn't allow this, stop and ask for help.
- [ ] **Wait 24–48 h**, then confirm the DS has left public DNS. Ask Claude to check, or run `dig DS automine.com.br`.
- [ ] **Registro.br → DNS servers:** replace `a.auto.dns.br` and `b.auto.dns.br` with the two Cloudflare nameservers. Save.
- [ ] Wait until the domain shows **Active** in Cloudflare (usually 1–2 h, and can take up to 24 h).

## 4. Cloudflare Pages: attach the custom domain (after Active)

- [ ] **Workers & Pages → automine → Custom domains → Add a custom domain** → `automine.com.br`. Cloudflare creates the proxied CNAME for the apex automatically. Don't create it by hand.
- [ ] Add `www.automine.com.br` the same way.
- [ ] Wait for both to show **Active**. Cloudflare issues the HTTPS certificates.
- [ ] Optional: redirect `www` to the apex. See "Redirecting www to domain apex" in the Pages docs.

## 5. Receive: Cloudflare Email Routing (free)

- [ ] **Email → Email Routing → Set up your domain.** Accept the automatic MX, SPF and DKIM records.
- [ ] **Destination addresses:** add the inbox that should receive leads (e.g. your Gmail), then click the verification link Cloudflare e-mails you. Rules stay disabled until you do.
- [ ] **Routing rules:** create `vendas@automine.com.br` → **Send to an email** → that inbox. Save.

Email Routing can't be used with external mail servers, so don't add MX records from another provider.

## 6. Send as vendas@ from Gmail: pick one option

Email Routing only *receives*. To send as `vendas@automine.com.br`, Gmail needs an SMTP server that is allowed to send for the domain.

### Option A: Cloudflare Email Sending (paid)

Requires the Workers **Paid** plan. Email Sending is in **beta**. It includes 3,000 e-mails a month, then US$0.35 per 1,000 (Cloudflare pricing page, as checked).

- [ ] Subscribe to Workers Paid. Then **Email Service → Email Sending** → add `automine.com.br`. Cloudflare adds its records on the `cf-bounce` subdomain automatically.
- [ ] Create an API token with the permission **Email Sending: Edit**. Don't paste it into chat.
- [ ] **Gmail → Settings → See all settings → Accounts and Import → Send mail as → Add another email address**:
  - Name: e.g. *Automine Vendas*. Address: `vendas@automine.com.br`. **Uncheck "Treat as an alias".**
  - SMTP server: `smtp.mx.cloudflare.net`, port `465`, **Secured connection using SSL**.
  - Username: `api_token` (the literal text). Password: the API token.
  - Gmail sends a confirmation code to `vendas@`. It arrives through Email Routing. Enter the code.

### Option B: free outside SMTP service

Some providers (for example Brevo) have free plans that include SMTP. Limits change, so check the provider's site before choosing.

- [ ] Create the account and authenticate `automine.com.br`. Add the DNS records their dashboard shows, in Cloudflare.
- [ ] If they require an SPF `include:`, add it to the **same** SPF record, e.g. `v=spf1 include:_spf.mx.cloudflare.net include:<their-include> ~all`. Only one SPF record is allowed, and SPF allows at most 10 DNS lookups.
- [ ] Set up Gmail's "Send mail as" the same way as Option A, using their host, port and credentials.

## 7. DNSSEC back on (optional)

- [ ] In Cloudflare, open the domain and enable **DNSSEC**. Copy the DS details it shows: key tag, algorithm 13, digest type 2, digest.
- [ ] **Registro.br → DNSSEC:** add the DS. Save.
- [ ] Ask Claude to verify the DS in public DNS. A wrong DS makes the domain fail for validating resolvers, so do this only after the tests pass.

## 8. Finish and test

- [ ] `https://automine.com.br` opens with HTTPS, and `www.automine.com.br` works too.
- [ ] Ask Claude to check public DNS. The apex should have A/AAAA (from Pages) and MX (from Email Routing) at the same time.
- [ ] From another account, send to `vendas@automine.com.br`. It should arrive within a minute or two. Gmail hides copies of messages you send to yourself, so a self-test looks like a failure.
- [ ] From Gmail, send *as* `vendas@` to another account, then **⋮ → Show original**. SPF, DKIM and DMARC should all say **PASS**.
- [ ] The site's "Enviar por e-mail" buttons and the contact form open the e-mail with the message ready.
- [ ] After a week with no problems, change `_dmarc` to `v=DMARC1; p=quarantine;`.

### Optional

- [ ] Add the site to Google Search Console and submit `https://automine.com.br/sitemap.xml`.
