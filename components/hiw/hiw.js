/* How It Works: client-side step navigator (no Streamlit reruns).
   State is kept in this script and mirrored on window.parent so it survives iframe reloads. */
(function () {
  'use strict';

  /* ---------- pure logic (unit-tested with node, see tests/test_hiw_logic.js) ---------- */
  var PROGRESS = [0.012, 0.25, 0.5, 1];            // ring fill per step; step 4 closes the loop
  function clampStep(n, total) { n = parseInt(n, 10); if (isNaN(n)) return 1; return Math.min(Math.max(n, 1), total); }
  function nextStep(s, total) { return Math.min(s + 1, total); }
  function prevStep(s) { return Math.max(s - 1, 1); }
  function progressFor(step) { return PROGRESS[clampStep(step, PROGRESS.length) - 1]; }
  function isEditableTag(tag) { tag = (tag || '').toLowerCase(); return tag === 'input' || tag === 'textarea' || tag === 'select'; }
  function isInteractiveTag(tag, role) {
    tag = (tag || '').toLowerCase(); role = (role || '').toLowerCase();
    return tag === 'button' || tag === 'a' || tag === 'summary' || role === 'button' || role === 'link' || role === 'tab' || role === 'menuitem';
  }
  /* Returns true only when ONE step should be advanced for this key event. */
  function shouldAdvanceOnEnter(i) {
    if (i.key !== 'Enter') return false;
    if (i.repeat || i.defaultPrevented) return false;
    if (i.ctrl || i.alt || i.meta || i.shift) return false;
    if (isEditableTag(i.targetTag) || i.targetEditable || i.targetRole === 'textbox' || i.targetRole === 'combobox' || i.targetRole === 'searchbox') return false;
    if (isInteractiveTag(i.targetTag, i.targetRole)) return false;   // native button/link activation handles it
    if (i.dialogOpen) return false;                                   // e.g. the EnergyBot dialog
    if (!i.sectionVisible) return false;                              // only while the section is on screen
    if (i.step >= i.total) return false;                              // step 4: never restart
    if (i.now - i.last < i.lockMs) return false;                      // one keypress = one step
    return true;
  }
  var api = { clampStep: clampStep, nextStep: nextStep, prevStep: prevStep, progressFor: progressFor, shouldAdvanceOnEnter: shouldAdvanceOnEnter, PROGRESS: PROGRESS };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; }
  if (typeof document === 'undefined' || !document.getElementById('hiw')) { return; }

  /* ---------- UI ---------- */
  var CFG = /*__CONFIG__*/ null;
  var STEPS = CFG.steps, TOTAL = STEPS.length, CIRC = 753.98;
  var root = document.getElementById('hiw');
  var $ = function (id) { return document.getElementById(id); };
  var stages = root.querySelectorAll('.stage'), nodes = root.querySelectorAll('.node');
  var prog = $('ringProg'), glow = $('ringGlow'), copy = $('copy');
  var P = null;
  try { P = window.parent && window.parent.document ? window.parent : null; } catch (e) { P = null; }

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var step = 1, lastAdvance = 0, inView = false, started = false;

  try { if (P && P.__ebaHiw && P.__ebaHiw.step) step = clampStep(P.__ebaHiw.step, TOTAL); } catch (e) {}
  function persist() { try { if (P) P.__ebaHiw = { step: step }; } catch (e) {} }

  function render(dir) {
    root.setAttribute('data-step', String(step));
    root.classList.toggle('complete', step === TOTAL);
    var p = progressFor(step);
    prog.style.strokeDashoffset = String(CIRC * (1 - p));
    glow.style.strokeDashoffset = '0';
    root.setAttribute('data-progress', String(p));
    for (var i = 0; i < stages.length; i++) {
      var n = i + 1;
      stages[i].classList.toggle('active', n === step);
      stages[i].classList.toggle('before', n < step);
    }
    for (var j = 0; j < nodes.length; j++) {
      var m = j + 1;
      nodes[j].classList.toggle('active', m === step);
      nodes[j].classList.toggle('done', m < step || (m === TOTAL && step === TOTAL));
      if (m === step) nodes[j].setAttribute('aria-current', 'step'); else nodes[j].removeAttribute('aria-current');
    }
    var s = STEPS[step - 1];
    $('title').textContent = s.title;
    $('desc').textContent = s.desc;
    $('badge').textContent = 'Step ' + step + ' · ' + s.label;
    $('count').textContent = step === TOTAL ? 'Step ' + TOTAL + ' of ' + TOTAL + ' · Done' : 'Step ' + step + ' of ' + TOTAL;
    $('prev').disabled = step === 1;
    $('next').disabled = step === TOTAL;
    $('next').textContent = step === TOTAL - 1 ? 'Next: ' + STEPS[TOTAL - 1].label : 'Next';
    $('restart').style.visibility = step > 1 ? 'visible' : 'hidden';
    $('ctaBtn').textContent = CFG.cta;
    $('hint').innerHTML = step === TOTAL
      ? 'You\u2019ve seen every step. Use Previous to revisit one, or Restart to begin again.'
      : 'Press <kbd>Enter</kbd> or choose Next to continue. Enter is ignored while you type in a field.';
    $('live').textContent = 'Step ' + step + ' of ' + TOTAL + ': ' + s.title;
    if (!reduce && dir !== 0) { copy.classList.remove('swap'); void copy.offsetWidth; copy.classList.add('swap'); }
    persist();
    fit();
  }
  function go(n, dir) {
    n = clampStep(n, TOTAL);
    if (n === step) return;
    var d = n > step ? 1 : -1;
    step = n; render(d);
  }
  function advance() { var n = nextStep(step, TOTAL); if (n !== step) { lastAdvance = Date.now(); go(n); } }

  /* confetti for the completion moment (decorative, one-shot) */
  (function () {
    var box = root.querySelector('.confetti'), cols = ['#2563eb', '#06b6d4', '#10b981', '#7c3aed', '#f59e0b'];
    for (var i = 0; i < 12; i++) {
      var a = (i / 12) * Math.PI * 2, r = 70 + (i % 3) * 18, el = document.createElement('i');
      el.style.background = cols[i % cols.length];
      el.style.setProperty('--x', Math.round(Math.cos(a) * r) + 'px');
      el.style.setProperty('--y', Math.round(Math.sin(a) * r) + 'px');
      el.style.animationDelay = (0.85 + (i % 4) * 0.04) + 's';
      box.appendChild(el);
    }
  })();

  /* controls */
  $('next').addEventListener('click', function () { advance(); });
  $('prev').addEventListener('click', function () { go(prevStep(step)); });
  $('restart').addEventListener('click', function () { go(1); });
  for (var k = 0; k < nodes.length; k++) {
    (function (btn) { btn.addEventListener('click', function () { go(btn.getAttribute('data-go')); }); })(nodes[k]);
  }
  $('ctaBtn').addEventListener('click', function () {
    var target = null;
    try { target = P && P.document.querySelector('.st-key-hiw_start button'); } catch (e) {}
    if (target) { target.click(); }
    else { try { P.location.hash = 'providers'; } catch (e) {} }
  });

  /* keyboard: Enter advances exactly one step, only while the section is on screen and nobody is typing */
  function visibleRatio() {
    try {
      var fe = window.frameElement;
      if (!fe || !P) return inView ? 1 : 0;
      var r = fe.getBoundingClientRect(), vh = P.innerHeight || 800;
      var vis = Math.min(r.bottom, vh) - Math.max(r.top, 0);
      return Math.max(0, vis) / Math.max(1, Math.min(r.height, vh));
    } catch (e) { return inView ? 1 : 0; }
  }
  function onKey(doc) {
    return function (e) {
      var t = e.target || {};
      var role = t.getAttribute ? t.getAttribute('role') : '';
      var dialog = false;
      try { dialog = !!(P && P.document.querySelector('[role="dialog"], [data-testid="stDialog"]')); } catch (x) {}
      var ok = shouldAdvanceOnEnter({
        key: e.key, repeat: e.repeat, defaultPrevented: e.defaultPrevented, ctrl: e.ctrlKey, alt: e.altKey, meta: e.metaKey, shift: e.shiftKey,
        targetTag: t.tagName, targetEditable: !!t.isContentEditable, targetRole: role, dialogOpen: dialog,
        sectionVisible: visibleRatio() >= 0.5 && document.visibilityState !== 'hidden',
        step: step, total: TOTAL, now: Date.now(), last: lastAdvance, lockMs: 250
      });
      if (ok) { e.preventDefault(); advance(); }
    };
  }
  document.addEventListener('keydown', onKey(document));
  try {
    if (P) {
      if (P.__ebaEnterHandler) { P.document.removeEventListener('keydown', P.__ebaEnterHandler); }
      var h = function (e) {
        if (!window.frameElement || !window.frameElement.isConnected) { P.document.removeEventListener('keydown', h); return; }
        onKey(P.document)(e);
      };
      P.__ebaEnterHandler = h;
      P.document.addEventListener('keydown', h);
      window.addEventListener('pagehide', function () { try { P.document.removeEventListener('keydown', h); } catch (e) {} });
    }
  } catch (e) { /* cross-origin parent: Enter still works when this component has focus */ }

  /* start animations when the section first scrolls into view (state is kept afterwards) */
  function start() { if (!started) { started = true; root.classList.add('live'); } }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (en) { inView = en.isIntersecting; if (en.isIntersecting) start(); });
    }, { threshold: 0.25 }).observe(root);
  } else { start(); }

  /* size the iframe to its content */
  var lastH = 0;
  function fit() {
    try {
      var fe = window.frameElement; if (!fe) return;
      var h = Math.ceil(root.getBoundingClientRect().height) + 2;
      if (Math.abs(h - lastH) > 1) { lastH = h; fe.style.height = h + 'px'; fe.setAttribute('height', String(h)); }
    } catch (e) {}
  }
  if ('ResizeObserver' in window) { new ResizeObserver(fit).observe(root); }
  window.addEventListener('resize', fit);

  window.__eba = { get step() { return step; }, goTo: go, next: advance, prev: function () { go(prevStep(step)); } };
  render(0);
})();
