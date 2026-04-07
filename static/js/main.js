/* main.js — AI in Education */

/* ── Hamburger navigation ─────────────────────────────────── */
(function () {
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.getElementById('nav-links');
  if (!toggle || !navLinks) return;

  toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!expanded));
    navLinks.classList.toggle('open', !expanded);
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!toggle.contains(e.target) && !navLinks.contains(e.target)) {
      toggle.setAttribute('aria-expanded', 'false');
      navLinks.classList.remove('open');
    }
  });

  // Close when a nav link is clicked
  navLinks.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      toggle.setAttribute('aria-expanded', 'false');
      navLinks.classList.remove('open');
    });
  });
})();

/* ── Q&A accordion ────────────────────────────────────────── */
(function () {
  document.querySelectorAll('.qa-trigger').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const answer = trigger.nextElementSibling;
      const isOpen = trigger.getAttribute('aria-expanded') === 'true';

      if (isOpen) {
        collapse(trigger, answer);
      } else {
        expand(trigger, answer);
      }
    });
  });

  function expand(trigger, answer) {
    trigger.setAttribute('aria-expanded', 'true');
    answer.hidden = false;
    // Animate height
    const height = answer.scrollHeight;
    answer.style.maxHeight = '0';
    answer.style.overflow = 'hidden';
    answer.style.transition = 'max-height 0.3s ease';
    requestAnimationFrame(() => {
      answer.style.maxHeight = height + 'px';
    });
    answer.addEventListener('transitionend', () => {
      answer.style.maxHeight = '';
      answer.style.overflow = '';
      answer.style.transition = '';
    }, { once: true });
  }

  function collapse(trigger, answer) {
    trigger.setAttribute('aria-expanded', 'false');
    const height = answer.scrollHeight;
    answer.style.maxHeight = height + 'px';
    answer.style.overflow = 'hidden';
    answer.style.transition = 'max-height 0.25s ease';
    requestAnimationFrame(() => {
      answer.style.maxHeight = '0';
    });
    answer.addEventListener('transitionend', () => {
      answer.hidden = true;
      answer.style.maxHeight = '';
      answer.style.overflow = '';
      answer.style.transition = '';
    }, { once: true });
  }
})();

/* ── Active nav link highlight ────────────────────────────── */
(function () {
  const currentUrl = window.location.href.split('#')[0]; // Remove hash
  document.querySelectorAll('.nav-link').forEach((link) => {
    link.classList.remove('active');
    const linkUrl = link.href.split('#')[0]; // Remove hash
    if (linkUrl === currentUrl) {
      link.classList.add('active');
    }
  });
})();
