(() => {
  const carousel = document.querySelector('[data-review-carousel]');
  if (!carousel) return;
  const viewport = carousel.querySelector('.feedback-carousel__viewport');
  const slides = [...carousel.querySelectorAll('.feedback-card')];
  const dots = [...carousel.querySelectorAll('[data-review-index]')];
  const arrows = [...carousel.querySelectorAll('[data-review-step]')];
  const count = carousel.querySelector('[data-review-count]');
  const status = carousel.querySelector('[data-review-status]');
  const controls = carousel.querySelector('.feedback-editorial__controls');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let active = 0, frame = 0, timer;
  const visible = () => Number(getComputedStyle(carousel).getPropertyValue('--visible')) || 1;
  const max = () => Math.max(0, slides.length - visible());
  const step = () => slides[0].getBoundingClientRect().width + 18;
  const update = (announce = false) => {
    arrows.forEach(b => { b.disabled = Number(b.dataset.reviewStep) < 0 ? active === 0 : active === max(); });
    dots.forEach((dot, i) => { dot.hidden = i > max(); dot.setAttribute('aria-pressed', String(i === active)); });
    count.textContent = String(active + 1).padStart(2, '0');
    slides.forEach((slide, i) => { slide.inert = i < active || i >= active + visible(); });
    if (announce) status.textContent = `Reviews ${active + 1} to ${Math.min(slides.length, active + visible())} of ${slides.length}.`;
  };
  const show = (index, animate = true) => {
    cancelAnimationFrame(frame);
    active = Math.max(0, Math.min(max(), index));
    const from = viewport.scrollLeft, to = active * step();
    const started = performance.now();
    viewport.style.scrollSnapType = 'none';
    const tick = now => {
      const progress = animate && !reduced.matches ? Math.min(1, (now - started) / 520) : 1;
      viewport.scrollLeft = from + (to - from) * (1 - Math.pow(1 - progress, 3));
      if (progress < 1) frame = requestAnimationFrame(tick);
      else { frame = 0; viewport.style.scrollSnapType = ''; update(animate); }
    };
    update(false);
    frame = requestAnimationFrame(tick);
  };
  arrows.forEach(button => { controls.append(button); button.hidden = false; button.addEventListener('click', () => show(active + Number(button.dataset.reviewStep))); });
  dots.forEach(dot => dot.addEventListener('click', () => show(Number(dot.dataset.reviewIndex))));
  carousel.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.target.closest('a,input,textarea,select')) return;
    const positions = { ArrowLeft: active - 1, ArrowRight: active + 1, Home: 0, End: max() };
    if (event.key in positions) { event.preventDefault(); show(positions[event.key]); }
  });
  const cancel = () => { cancelAnimationFrame(frame); frame = 0; viewport.style.scrollSnapType = ''; };
  viewport.addEventListener('pointerdown', cancel, { passive: true });
  viewport.addEventListener('wheel', cancel, { passive: true });
  viewport.addEventListener('scroll', () => {
    clearTimeout(timer);
    timer = setTimeout(() => { if (!frame) { active = Math.min(max(), Math.max(0, Math.round(viewport.scrollLeft / step()))); update(true); } }, 120);
  }, { passive: true });
  new ResizeObserver(() => show(active, false)).observe(viewport);
  slides.forEach((slide, i) => { slide.setAttribute('role', 'group'); slide.setAttribute('aria-roledescription', 'slide'); slide.setAttribute('aria-label', `Review ${i + 1} of ${slides.length}`); });
  carousel.setAttribute('aria-roledescription', 'carousel');
  carousel.tabIndex = 0;
  carousel.querySelector('.feedback-carousel__pager').hidden = false;
  show(0, false);
})();
