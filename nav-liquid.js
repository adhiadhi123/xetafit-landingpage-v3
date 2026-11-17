(() => {
  const links = [...document.querySelectorAll('.hdr__nav a')];
  const sections = links.map(link => document.querySelector(link.hash));
  const select = selected => links.forEach(link => {
    if (link === selected) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  const controls = links;
  controls.forEach(link => {

    const liquid = document.createElement('span');
    liquid.className = 'nav-liquid';
    liquid.setAttribute('aria-hidden', 'true');
    const wave = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    wave.classList.add('nav-wave');
    wave.setAttribute('viewBox', '0 0 600 12');
    wave.setAttribute('preserveAspectRatio', 'none');
    wave.setAttribute('focusable', 'false');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    let curve = 'M0 6';
    for (let x = 0; x < 600; x += 100) {
      curve += ` C${x + 16.667} 0 ${x + 33.333} 0 ${x + 50} 6`;
      curve += ` C${x + 66.667} 12 ${x + 83.333} 12 ${x + 100} 6`;
    }
    path.setAttribute('d', curve + ' V12 H0 Z');
    wave.append(path);
    liquid.append(wave);
    link.prepend(liquid);
    if (links.includes(link)) link.addEventListener('click', () => select(link));
  });
  let pending = false;
  function update() {
    pending = false;
    const line = window.innerHeight * .4;
    const index = sections.findIndex(section => {
      if (!section) return false;
      const bounds = section.getBoundingClientRect();
      return bounds.top <= line && bounds.bottom > line;
    });
    select(links[index]);
  }
  window.addEventListener('scroll', () => {
    if (!pending) { pending = true; requestAnimationFrame(update); }
  }, { passive: true });
  window.addEventListener('resize', update);
  update();
})();
// CTA feedback never intercepts a destination or a form action.
(() => {
  const calm = matchMedia('(prefers-reduced-motion: reduce)');
  const rand = (min, max) => min + Math.random() * (max - min);
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  // Hover current: wave cross-sections at a 50px-tall CTA, scaled to each button.
  // Mostly small and medium; larger waves are rarer and fainter.
  const TIERS = [
    { min: 8, max: 12, odds: .5, peak: [.15, .21] },
    { min: 14, max: 20, odds: .38, peak: [.11, .16] },
    { min: 22, max: 28, odds: .12, peak: [.08, .11] }
  ];
  const MAX_WAVES = 6;     // live wave elements per button
  const COVERAGE = .2;     // wave footprints may claim at most this share of the button

  document.querySelectorAll('.btn, .hdr__cta').forEach(button => {
    button.classList.add('cta-water');
    const liquid = document.createElement('span');
    liquid.className = 'cta-water__liquid';
    liquid.setAttribute('aria-hidden', 'true');
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 240 120');
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.setAttribute('focusable', 'false');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M0 64C4 42 24 48 40 28C58 5 76 30 98 16C120 0 136 28 156 20C182 8 184 46 210 38C232 32 244 62 236 78C224 104 202 84 182 104C158 124 146 96 122 108C98 120 78 92 58 102C30 114 28 82 10 86C0 88 -2 76 0 64Z');
    // Flatten the liquid curve very slightly (about 1–2px at normal CTA sizes).
    path.setAttribute('transform', 'translate(0 1.2) scale(1 .98)');
    svg.append(path);
    liquid.append(svg);
    button.prepend(liquid);
    let animation;
    function play(event, centered = false) {
      if (button.matches(':disabled, [aria-disabled="true"]')) return;
      const rect = button.getBoundingClientRect();
      const x = centered ? rect.width / 2 : Math.max(0, Math.min(rect.width, event.clientX - rect.left));
      const y = centered ? rect.height / 2 : Math.max(0, Math.min(rect.height, event.clientY - rect.top));
      liquid.style.left = `${x}px`;
      liquid.style.top = `${y}px`;
      liquid.style.width = `${rect.width * 3}px`;
      liquid.style.height = `${rect.height * 4}px`;
      animation?.cancel();
      const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
      const frames = reduceMotion ? [
        { opacity: 0 }, { opacity: .12, offset: .2 }, { opacity: 0 }
      ] : [
        { transform: 'translate(-50%, -50%) scale(.015, .05) rotate(-12deg)', opacity: 0 },
        { transform: 'translate(-50%, -50%) scale(.22, .4) rotate(-7deg)', opacity: .16, offset: .16 },
        { transform: 'translate(-50%, -50%) scale(.7, .8) rotate(2deg)', opacity: .2, offset: .45 },
        { transform: 'translate(-50%, -50%) scale(1, 1) rotate(0deg)', opacity: .14, offset: .7 },
        { transform: 'translate(-50%, -50%) scale(1.06, .95) rotate(0deg)', opacity: 0 }
      ];
      animation = liquid.animate(frames, {
        duration: reduceMotion ? 160 : 800,
        easing: 'cubic-bezier(.22,.61,.36,1)'
      });
    }
    // Pointerdown starts before native navigation; click handles keyboard/AT once.
    button.addEventListener('pointerdown', event => {
      if (event.isPrimary && event.button === 0) play(event);
    });
    button.addEventListener('click', event => {
      if (event.detail === 0) play(event, true);
    });

    // Hover current: a few organic waves trail the pointer and drift with it.
    const flow = document.createElement('span');
    flow.className = 'cta-water__flow';
    flow.setAttribute('aria-hidden', 'true');
    liquid.after(flow);
    const waves = new Map();
    let px = 0, py = 0, pt = 0;            // latest pointer sample (viewport px, ms)
    let lx, ly, lt;                        // previous sample in button space
    let hx = 1, hy = 0, speed = 0;         // smoothed heading and speed
    let travelled = 0, gap = 0, lastSpawn = -1e4, lastTier = 0, frame = 0, dragging = false, boost = 1;

    // Water reads as a tint that contrasts with the hover fill: apple green over a
    // white fill, white glints over green fills. Ghost buttons keep their text colour.
    function tint() {
      if (button.classList.contains('btn--ghost')) { flow.style.color = ''; boost = 1.15; return; }
      const fill = getComputedStyle(button).getPropertyValue('--b-hover').replace(/\s/g, '').toLowerCase();
      const white = ['#fff', '#ffffff', 'white', 'rgb(255,255,255)'].includes(fill);
      flow.style.color = white ? 'var(--color-primary)' : 'var(--color-secondary)';
      boost = white ? 1.3 : 1.1;
    }

    function clear() {
      waves.forEach((wave, node) => { wave.anims.forEach(anim => anim.cancel()); node.remove(); });
      waves.clear();
    }
    function settle() {
      cancelAnimationFrame(frame);
      frame = 0;
      lx = undefined;
      flow.classList.add('is-leaving');
    }
    function track(event) {
      if (flow.classList.contains('is-leaving')) {
        clear();
        flow.classList.remove('is-leaving');
        travelled = 0;
        gap = rand(6, 12);
      }
      px = event.clientX;
      py = event.clientY;
      pt = event.timeStamp;
      if (!frame) frame = requestAnimationFrame(step);
    }
    function step() {
      frame = 0;
      if (calm.matches || button.matches(':disabled, [aria-disabled="true"]')) return;
      const rect = button.getBoundingClientRect();
      const x = px - rect.left - button.clientLeft;
      const y = py - rect.top - button.clientTop;
      if (lx === undefined) { lx = x; ly = y; lt = pt; return; }
      const dx = x - lx, dy = y - ly, dist = Math.hypot(dx, dy);
      if (dist < .5) return;
      const dt = Math.max(8, pt - lt);
      lx = x; ly = y; lt = pt;
      // The heading eases toward the new direction, so reversals bend rather than snap.
      hx += (dx / dist - hx) * .45;
      hy += (dy / dist - hy) * .45;
      speed += (dist / dt - speed) * .35;
      travelled += dist;
      if (travelled < gap || pt - lastSpawn < 55) return;
      const norm = Math.hypot(hx, hy) || 1;
      if (spawn(x, y, hx / norm, hy / norm, rect)) {
        travelled = 0;
        gap = rand(14, 30) * clamp(rect.height / 50, .8, 1.06);
        lastSpawn = pt;
      }
    }
    function spawn(x, y, ux, uy, rect) {
      if (waves.size >= MAX_WAVES) return false;
      const w = button.clientWidth, h = button.clientHeight;
      const scale = clamp(rect.height / 50, .8, 1.06);
      // Weighted size pick; a large wave never follows another large one.
      const roll = Math.random() * (lastTier === 2 ? TIERS[0].odds + TIERS[1].odds : 1);
      let tier = roll < TIERS[0].odds ? 0 : roll < TIERS[0].odds + TIERS[1].odds ? 1 : 2;
      let cross = rand(TIERS[tier].min, TIERS[tier].max) * scale;
      let length = cross * rand(1.35, 1.9);
      let used = 0;
      waves.forEach(wave => { used += wave.footprint; });
      const budget = COVERAGE * w * h;
      if (used + Math.PI / 4 * cross * length > budget) {
        if (tier === 0) return false;
        tier = 0;
        cross = rand(TIERS[0].min, TIERS[0].max) * scale;
        length = cross * rand(1.35, 1.9);
        if (used + Math.PI / 4 * cross * length > budget) return false;
      }
      lastTier = tier;

      // Start a little behind the cursor, off its exact line, then glide forward.
      const trail = rand(3, 9) * scale;
      const side = rand(-1, 1) * h * .14;
      const x0 = x - ux * trail - uy * side;
      const y0 = clamp(y - uy * trail + ux * side, h * .22, h * .78);
      const heading = Math.atan2(uy, ux) + rand(-.2, .2);
      const reach = clamp(8 + speed * 28, 10, 26) * scale * rand(.8, 1.15);
      const bow = rand(-3, 3) * scale;
      const cos = Math.cos(heading), sin = Math.sin(heading);
      const xm = x0 + cos * reach * .5 - sin * bow, ym = y0 + sin * reach * .5 + cos * bow;
      const x1 = x0 + cos * reach, y1 = y0 + sin * reach;

      const response = rand(100, 160), travel = rand(350, 550), dissipate = rand(300, 450);
      const total = travel + dissipate * .6;
      const fadeFrom = total - dissipate;
      const peak = rand(...TIERS[tier].peak) * boost;
      const angle = heading * 180 / Math.PI;
      const turn = rand(-7, 7);

      const node = document.createElement('span');
      node.className = 'cta-water__wave';
      const body = document.createElement('span');
      // Uneven corner radii give each crest its own curvature; the tail tapers behind it.
      const top = rand(52, 66), bottom = rand(52, 66), left = rand(40, 60), right = rand(38, 62);
      // The crest arc peaks between 88% and 112% of the length, with a different bend each time.
      const ex = rand(130, 170), cx = rand(88, 112) - ex * .86;
      body.style.cssText = `--l:${length.toFixed(1)}px;--c:${cross.toFixed(1)}px;--hx:${rand(56, 70).toFixed(0)}%;` +
        `--ex:${ex.toFixed(0)}%;--ey:${rand(84, 100).toFixed(0)}%;--cx:${cx.toFixed(0)}%;` +
        `--r:${top.toFixed(0)}% ${(100 - top).toFixed(0)}% ${(100 - bottom).toFixed(0)}% ${bottom.toFixed(0)}% / ` +
        `${left.toFixed(0)}% ${right.toFixed(0)}% ${(100 - right).toFixed(0)}% ${(100 - left).toFixed(0)}%`;
      node.append(body);
      flow.append(node);

      const glide = node.animate([
        { transform: `translate(${x0}px, ${y0}px)` },
        { transform: `translate(${xm}px, ${ym}px)`, offset: .5 },
        { transform: `translate(${x1}px, ${y1}px)` }
      ], { duration: total, easing: 'cubic-bezier(.22,.61,.36,1)' });
      const shape = body.animate([
        { opacity: 0, transform: `rotate(${angle}deg) scale(.45, .6)`, easing: 'cubic-bezier(.3,.7,.4,1)' },
        { opacity: peak, transform: `rotate(${angle + turn * .3}deg) scale(.82, .9)`, offset: response / total },
        { opacity: peak * .85, transform: `rotate(${angle + turn * .75}deg) scale(1, 1)`, offset: fadeFrom / total, easing: 'cubic-bezier(.4,0,.6,1)' },
        { opacity: 0, transform: `rotate(${angle + turn}deg) scale(1.12, 1.05)` }
      ], { duration: total });
      waves.set(node, { footprint: Math.PI / 4 * cross * length, anims: [glide, shape] });
      shape.onfinish = () => { waves.delete(node); node.remove(); };
      return true;
    }

    button.addEventListener('pointerenter', event => {
      if (event.pointerType === 'touch') return;
      dragging = false;
      travelled = 0;
      gap = rand(6, 12);
      tint();
    });
    button.addEventListener('pointermove', event => {
      if (event.pointerType !== 'touch') track(event);
    });
    // A native link drag cancels pointer events; dragover keeps the current following.
    button.addEventListener('pointercancel', event => {
      if (event.pointerType === 'mouse') dragging = true;
    });
    button.addEventListener('pointerleave', event => {
      if (event.pointerType !== 'touch' && !dragging) settle();
    });
    button.addEventListener('dragover', track);
    button.addEventListener('dragleave', event => {
      if (!button.contains(event.relatedTarget)) { dragging = false; settle(); }
    });
    button.addEventListener('dragend', () => { dragging = false; settle(); });
  });
})();