/* Automine — interações da landing page (sem dependências) */
(() => {
  'use strict';

  /* ------------------------------------------------------------------
   * Contatos — altere aqui se o número ou o e-mail mudarem.
   * (Os links no HTML também apontam para estes valores, para funcionar
   * mesmo sem JavaScript.)
   * ---------------------------------------------------------------- */
  const CONTACT = {
    whatsapp: '5511911468446',
    email: 'vendas@automine.com.br',
  };

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
  const int = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });

  const waLink = (text) =>
    `https://wa.me/${CONTACT.whatsapp}${text ? `?text=${encodeURIComponent(text)}` : ''}`;

  const mailLink = (subject, body) => {
    const params = [];
    if (subject) params.push(`subject=${encodeURIComponent(subject)}`);
    if (body) params.push(`body=${encodeURIComponent(body.replace(/\r?\n/g, '\r\n'))}`);
    return `mailto:${CONTACT.email}${params.length ? `?${params.join('&')}` : ''}`;
  };

  const openExternal = (url) => {
    const win = window.open(url, '_blank');
    if (win) win.opener = null;
    else window.location.href = url;
  };

  /* ------------------------------------------------------------ toast */
  const toastEl = document.querySelector('[data-toast]');
  let toastTimer;
  const toast = (message) => {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove('is-visible'), 2800);
  };

  /* ----------------------------------- links com mensagem pré-preenchida */
  document.querySelectorAll('[data-wa]').forEach((a) => {
    a.href = waLink(a.dataset.wa);
  });

  document.querySelectorAll('[data-mail-subject]').forEach((a) => {
    a.href = mailLink(a.dataset.mailSubject, a.dataset.mailBody);
  });

  /* ------------------------------------------------------------- ano */
  document.querySelectorAll('[data-year]').forEach((el) => {
    el.textContent = String(new Date().getFullYear());
  });

  /* ------------------------------------------------------- cabeçalho */
  const header = document.querySelector('[data-header]');

  /* ---------------------------------------------------- menu móvel */
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const menu = document.getElementById('menu-mobile');

  const setMenu = (open) => {
    if (!menuToggle || !menu) return;
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    menu.hidden = !open;
    document.body.classList.toggle('menu-open', open);
    if (open) menu.querySelector('a')?.focus();
  };

  menuToggle?.addEventListener('click', () => setMenu(menu.hidden));
  menu?.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menu && !menu.hidden) {
      setMenu(false);
      menuToggle.focus();
    }
  });
  window.matchMedia('(min-width: 1000px)').addEventListener('change', (event) => {
    if (event.matches) setMenu(false);
  });

  /* ------------------------------------------------ revelar ao rolar */
  const revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in');
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.12 },
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }

  /* ---------------- trilho lateral, menu ativo e linha do tempo */
  const sections = [...document.querySelectorAll('[data-rail]')];
  const rail = document.querySelector('[data-rail-el]');
  const railNum = rail?.querySelector('[data-rail-num]');
  const railLabel = rail?.querySelector('[data-rail-label]');
  const navLinks = [...document.querySelectorAll('.nav__list a')];
  const timeline = document.querySelector('[data-timeline]');
  const steps = timeline ? [...timeline.querySelectorAll('.step')] : [];
  const stepNodes = steps.map((step) => step.querySelector('.step__node'));

  // Todas as leituras de layout primeiro, depois todas as escritas (evita reflow forçado).
  const update = () => {
    const vh = window.innerHeight;
    const scrollY = window.scrollY;
    const probe = vh * 0.4;
    const current = sections.find((s) => {
      const r = s.getBoundingClientRect();
      return r.top <= probe && r.bottom > probe;
    });
    const maxScroll = document.documentElement.scrollHeight - vh;
    const line = vh * 0.62;
    let progress = 0;
    let activeSteps = [];
    if (timeline) {
      const r = timeline.getBoundingClientRect();
      progress = Math.min(1, Math.max(0, (line - r.top) / r.height));
      activeSteps = stepNodes.map((node) => {
        const n = node.getBoundingClientRect();
        return n.top + n.height / 2 < line;
      });
    }

    header?.classList.toggle('is-scrolled', scrollY > 12);

    if (rail) {
      if (current) {
        const [num, label] = current.dataset.rail.split('|');
        if (railNum.textContent !== num) railNum.textContent = num;
        if (railLabel.textContent !== label) railLabel.textContent = label;
      }
      rail.classList.toggle('is-visible', Boolean(current));
      rail.style.setProperty('--p', maxScroll > 0 ? (scrollY / maxScroll).toFixed(3) : '0');
    }

    navLinks.forEach((a) => {
      a.classList.toggle('is-active', Boolean(current) && a.hash === `#${current.id}`);
    });

    if (timeline) {
      timeline.style.setProperty('--progress', progress.toFixed(3));
      steps.forEach((step, i) => step.classList.toggle('is-active', activeSteps[i]));
    }
  };

  let ticking = false;
  const requestUpdate = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      update();
      ticking = false;
    });
  };
  window.addEventListener('scroll', requestUpdate, { passive: true });
  window.addEventListener('resize', requestUpdate);
  // Primeira leitura só depois do primeiro quadro desenhado, com o layout já calculado.
  requestAnimationFrame(() => setTimeout(update, 0));

  /* ------------------------------------- parallax sutil no herói */
  const art = document.querySelector('[data-parallax]');
  if (art && !reduceMotion && window.matchMedia('(pointer: fine)').matches) {
    const layers = [...art.querySelectorAll('[data-depth]')];
    const hero = art.closest('section');
    hero.addEventListener('pointermove', (event) => {
      const x = event.clientX / window.innerWidth - 0.5;
      const y = event.clientY / window.innerHeight - 0.5;
      layers.forEach((layer) => {
        const depth = Number(layer.dataset.depth);
        layer.style.translate = `${(x * depth).toFixed(1)}px ${(y * depth).toFixed(1)}px`;
      });
    });
    hero.addEventListener('pointerleave', () => {
      layers.forEach((layer) => {
        layer.style.translate = '';
      });
    });
  }

  /* ------------------------------------------------------ simulador */
  const sim = document.querySelector('[data-sim]');
  if (sim) {
    const MIN = 5000;
    const MAX = 2000000;
    const STEPS = 1000;
    const input = sim.querySelector('[data-sim-input]');
    const range = sim.querySelector('[data-sim-range]');
    const radios = [...sim.querySelectorAll('input[name="plano"]')];
    const out = (key) => sim.querySelector(`[data-out="${key}"]`);
    const waBtn = sim.querySelector('[data-sim-wa]');
    const mailBtn = sim.querySelector('[data-sim-mail]');

    const roundNice = (v) => {
      const step = v < 50000 ? 1000 : v < 500000 ? 5000 : 10000;
      return Math.round(v / step) * step;
    };
    const fromSlider = (s) => roundNice(MIN * (MAX / MIN) ** (s / STEPS));
    const toSlider = (v) =>
      Math.round((STEPS * Math.log(Math.min(MAX, Math.max(MIN, v)) / MIN)) / Math.log(MAX / MIN));
    const parse = (text) => Number(String(text).replace(/\D/g, '').slice(0, 12)) || 0;

    let amount = parse(input.value) || 100000;

    const render = () => {
      const plan = radios.find((r) => r.checked) || radios[1];
      const rate = Number(plan.dataset.rate);
      const fee = Math.round((amount * rate) / 100);
      const keep = amount - fee;

      out('keep').textContent = brl.format(keep);
      out('total').textContent = brl.format(amount);
      out('fee').textContent = brl.format(fee);
      out('rate').textContent = `${rate}%`;
      out('bar').style.setProperty('--keep', `${100 - rate}%`);

      const pos = toSlider(amount);
      range.value = String(pos);
      range.style.setProperty('--fill', `${(pos / STEPS) * 100}%`);
      range.setAttribute('aria-valuetext', brl.format(amount));

      const message =
        `Olá, Automine! Fiz uma simulação no site: economia estimada de ${brl.format(amount)} ` +
        `no plano ${plan.value} (${rate}% de comissão), ficando ${brl.format(keep)} no caixa da empresa. ` +
        'Gostaria de agendar um diagnóstico.';
      waBtn.href = waLink(message);
      mailBtn.href = mailLink(
        `Simulação de economia — plano ${plan.value}`,
        `Olá, equipe Automine!\n\n${message.replace('Olá, Automine! ', '')}\n\nNome:\nEmpresa:\nTelefone:`,
      );
    };

    input.addEventListener('input', () => {
      amount = parse(input.value);
      input.value = amount ? int.format(amount) : '';
      render();
    });
    input.addEventListener('blur', () => {
      if (!amount) amount = MIN;
      input.value = int.format(amount);
      render();
    });
    range.addEventListener('input', () => {
      amount = fromSlider(Number(range.value));
      input.value = int.format(amount);
      render();
    });
    radios.forEach((r) => r.addEventListener('change', render));

    input.value = int.format(amount);
    render();
  }

  /* -------------------------------------------------- formulário */
  const form = document.querySelector('[data-lead-form]');
  if (form) {
    let channel = 'whatsapp';
    form.querySelectorAll('button[type="submit"]').forEach((btn) => {
      btn.addEventListener('click', () => {
        channel = btn.value;
      });
    });

    const nameInput = form.elements.nome;
    const nameField = nameInput.closest('.field');
    const nameError = document.getElementById('f-nome-erro');

    const setNameError = (show) => {
      nameField.classList.toggle('is-invalid', show);
      nameError.hidden = !show;
      if (show) {
        nameInput.setAttribute('aria-invalid', 'true');
        nameInput.setAttribute('aria-describedby', 'f-nome-erro');
      } else {
        nameInput.removeAttribute('aria-invalid');
        nameInput.removeAttribute('aria-describedby');
      }
    };

    nameInput.addEventListener('input', () => {
      if (nameInput.value.trim()) setNameError(false);
    });

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const chosen = event.submitter?.value || channel;
      const value = (key) => (form.elements[key]?.value || '').trim();

      const name = value('nome');
      if (!name) {
        setNameError(true);
        nameInput.focus();
        return;
      }

      const company = value('empresa');
      const phone = value('telefone');
      const plan = value('plano');
      const message = value('mensagem');

      const lines = [
        'Olá, Automine! Gostaria de solicitar um diagnóstico.',
        '',
        `Nome: ${name}`,
        company ? `Empresa: ${company}` : null,
        phone ? `Telefone: ${phone}` : null,
        `Plano de interesse: ${plan}`,
        message ? `Mensagem: ${message}` : null,
      ].filter((line) => line !== null);
      const text = lines.join('\n');

      if (chosen === 'email') {
        toast('Abrindo o seu aplicativo de e-mail…');
        window.location.href = mailLink(`Solicitação de diagnóstico — ${company || name}`, text);
      } else {
        toast('Abrindo o WhatsApp…');
        openExternal(waLink(text));
      }
    });
  }

  /* --------------------------------------------- copiar e-mail */
  document.querySelectorAll('[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const text = btn.dataset.copy;
      try {
        await navigator.clipboard.writeText(text);
        toast('E-mail copiado!');
      } catch {
        toast(`Copie o e-mail: ${text}`);
      }
    });
  });
})();
