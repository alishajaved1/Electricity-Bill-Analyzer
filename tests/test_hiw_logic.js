// Run: node tests/test_hiw_logic.js
// Tests the pure step/keyboard logic, then drives the real hiw.js through a minimal fake DOM.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');
const dir = path.join(__dirname, '..', 'components', 'hiw');
const L = require(path.join(dir, 'hiw.js'));

// ---- pure logic ----
assert.strictEqual(L.clampStep(0, 4), 1); assert.strictEqual(L.clampStep(9, 4), 4); assert.strictEqual(L.clampStep('x', 4), 1);
assert.strictEqual(L.nextStep(4, 4), 4); assert.strictEqual(L.prevStep(1), 1);
assert.deepStrictEqual([1, 2, 3, 4].map(L.progressFor), [0.012, 0.25, 0.5, 1]);
const base = { key: 'Enter', repeat: false, defaultPrevented: false, ctrl: false, alt: false, meta: false, shift: false, targetTag: 'BODY', targetEditable: false,
  targetRole: '', dialogOpen: false, sectionVisible: true, step: 1, total: 4, now: 1000, last: 0, lockMs: 250 };
const t = (o) => L.shouldAdvanceOnEnter(Object.assign({}, base, o));
assert.ok(t({}));
assert.ok(!t({ key: 'a' })); assert.ok(!t({ repeat: true })); assert.ok(!t({ shift: true }));
assert.ok(!t({ targetTag: 'INPUT' })); assert.ok(!t({ targetTag: 'TEXTAREA' })); assert.ok(!t({ targetEditable: true })); assert.ok(!t({ targetRole: 'textbox' }));
assert.ok(!t({ targetTag: 'BUTTON' })); assert.ok(!t({ dialogOpen: true })); assert.ok(!t({ sectionVisible: false }));
assert.ok(!t({ step: 4 })); assert.ok(!t({ now: 1100, last: 1000 })); assert.ok(t({ now: 1300, last: 1000 }));

// ---- drive hiw.js with a fake DOM ----
function mkEl(id) {
  const cls = new Set(), attrs = {}, handlers = {};
  return { id, style: { setProperty() {} }, textContent: '', innerHTML: '', disabled: false, children: [], classList: {
      add: (c) => cls.add(c), remove: (c) => cls.delete(c), contains: (c) => cls.has(c),
      toggle: (c, on) => { (on === undefined ? !cls.has(c) : on) ? cls.add(c) : cls.delete(c); } },
    setAttribute: (k, v) => { attrs[k] = v; }, getAttribute: (k) => (k in attrs ? attrs[k] : null), removeAttribute: (k) => { delete attrs[k]; },
    addEventListener: (ev, fn) => { (handlers[ev] = handlers[ev] || []).push(fn); }, removeEventListener() {},
    appendChild(c) { this.children.push(c); }, querySelector: () => mkEl('q'), offsetWidth: 1,
    getBoundingClientRect: () => ({ top: 0, bottom: 600, height: 600 }), _h: handlers, _cls: cls, _attrs: attrs };
}
const els = {};
['ringProg', 'ringGlow', 'copy', 'title', 'desc', 'badge', 'count', 'prev', 'next', 'restart', 'ctaBtn', 'hint', 'live', 'hiw'].forEach((i) => (els[i] = mkEl(i)));
const stages = [1, 2, 3, 4].map(() => mkEl('s')), nodes = [1, 2, 3, 4].map((n) => { const e = mkEl('n'); e.setAttribute('data-go', String(n)); return e; });
els.hiw.querySelectorAll = (sel) => (sel === '.stage' ? stages : sel === '.node' ? nodes : []);
els.hiw.querySelector = () => mkEl('confetti');
const docHandlers = {};
const parentDocHandlers = {};
const parentDoc = { addEventListener: (e, f) => (parentDocHandlers[e] = f), removeEventListener() {}, querySelector: () => null };
const frame = { isConnected: true, style: {}, setAttribute() {}, getBoundingClientRect: () => ({ top: 0, bottom: 700, height: 700 }) };
const win = { parent: { document: parentDoc, innerHeight: 900 }, frameElement: frame, matchMedia: () => ({ matches: false }), addEventListener() {} };
const document = { getElementById: (i) => els[i], addEventListener: (e, f) => (docHandlers[e] = f), visibilityState: 'visible', createElement: () => mkEl('i') };
const cfg = { steps: [{ label: 'Upload', title: 'T1', desc: 'D1' }, { label: 'Verify', title: 'T2', desc: 'D2' }, { label: 'Review', title: 'T3', desc: 'D3' }, { label: 'Ask', title: 'T4', desc: 'D4' }], cta: 'Go' };
const src = fs.readFileSync(path.join(dir, 'hiw.js'), 'utf8').replace('/*__CONFIG__*/ null', JSON.stringify(cfg));
const ctx = { window: win, document, Date, Math, parseInt, isNaN, String, setTimeout, console };
win.window = win; vm.createContext(ctx); Object.assign(ctx, win); ctx.window = ctx; ctx.frameElement = frame; ctx.parent = win.parent; ctx.matchMedia = win.matchMedia;
vm.runInContext(src, ctx);
const eba = ctx.__eba; const step = () => eba.step;
const key = (o, where) => { let prevented = false; const e = Object.assign({ key: 'Enter', repeat: false, defaultPrevented: false, ctrlKey: false, altKey: false, metaKey: false, shiftKey: false,
  target: { tagName: 'BODY', isContentEditable: false, getAttribute: () => '' }, preventDefault() { prevented = true; } }, o);
  (where === 'iframe' ? docHandlers : parentDocHandlers).keydown(e); return prevented; };
// make the lock window pass between presses by faking time
let now = 10_000; const RealDate = Date; ctx.Date = { now: () => now };
const tick = () => { now += 400; };

assert.strictEqual(step(), 1); assert.strictEqual(els.hiw.getAttribute('data-step'), '1'); assert.strictEqual(els.title.textContent, 'T1');
assert.ok(els.prev.disabled); assert.ok(!els.next.disabled);
assert.ok(key({}, 'parent')); assert.strictEqual(step(), 2);                         // Enter -> exactly one step
assert.ok(!key({}, 'parent') && step() === 2);                                         // same instant: locked (no double advance)
tick(); key({ target: { tagName: 'INPUT', getAttribute: () => '' } }, 'parent'); assert.strictEqual(step(), 2);   // typing: ignored
tick(); key({ target: { tagName: 'TEXTAREA', getAttribute: () => '' } }, 'iframe'); assert.strictEqual(step(), 2);
tick(); key({ repeat: true }, 'parent'); assert.strictEqual(step(), 2);                // held key: ignored
tick(); key({}, 'iframe'); assert.strictEqual(step(), 3);
assert.strictEqual(els.ringProg.style.strokeDashoffset, String(753.98 * (1 - 0.5)));  // ring matches step 3
tick(); key({}, 'parent'); assert.strictEqual(step(), 4);
assert.strictEqual(els.ringProg.style.strokeDashoffset, '0');                          // ring complete on step 4
assert.ok(els.hiw._cls.has('complete')); assert.ok(els.next.disabled);
tick(); assert.ok(!key({}, 'parent')); assert.strictEqual(step(), 4);                  // Enter at step 4: no restart
els.prev._h.click[0](); assert.strictEqual(step(), 3);                                 // Previous
els.next._h.click[0](); assert.strictEqual(step(), 4);                                 // Next button
nodes[1]._h.click[0](); assert.strictEqual(step(), 2);                                 // click a step number
assert.ok(nodes[0]._cls.has('done') && nodes[1]._cls.has('active'));
els.restart._h.click[0](); assert.strictEqual(step(), 1);                              // intentional restart
assert.strictEqual(ctx.parent.__ebaHiw.step, 1);                                       // state mirrored for iframe reloads
// section off-screen -> Enter ignored
frame.getBoundingClientRect = () => ({ top: 2000, bottom: 2700, height: 700 }); tick(); key({}, 'parent'); assert.strictEqual(step(), 1);
frame.getBoundingClientRect = () => ({ top: 0, bottom: 700, height: 700 });
// dialog open -> ignored
parentDoc.querySelector = () => ({}); tick(); key({}, 'parent'); assert.strictEqual(step(), 1);
console.log('hiw logic + fake-DOM tests: all passed');
