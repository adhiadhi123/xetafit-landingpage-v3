(() => {
  const gallery = document.querySelector('.product-gallery');
  if (!gallery) return;
  const track = gallery.querySelector('.product-gallery__track');
  const slides = [...track.children];
  const thumbs = [...gallery.querySelectorAll('[data-slide]')];
  const previous = gallery.querySelector('[data-gallery-prev]');
  const next = gallery.querySelector('[data-gallery-next]');
  const status = gallery.querySelector('.product-gallery__status');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let current = 0;
  let frame;
  let timer;
  let inView = false;
  function update() {
    current = Math.max(0, Math.min(slides.length - 1, Math.round(track.scrollLeft / track.clientWidth)));
    thumbs.forEach((thumb, i) => thumb.setAttribute('aria-pressed', String(i === current)));
    previous.disabled = current === 0;
    next.disabled = current === slides.length - 1;
    status.textContent = `${String(current + 1).padStart(2, '0')} / ${slides.length}`;
    const strip = gallery.querySelector('.product-gallery__thumbs');
    const selected = thumbs[current];
    const left = selected.offsetLeft - strip.offsetLeft;
    if (left < strip.scrollLeft) strip.scrollLeft = left;
    else if (left + selected.offsetWidth > strip.scrollLeft + strip.clientWidth) {
      strip.scrollLeft = left + selected.offsetWidth - strip.clientWidth;
    }
  }
  function go(index, instant = reduced.matches) {
    const target = Math.max(0, Math.min(slides.length - 1, index));
    track.scrollTo({left:target * track.clientWidth, behavior:instant ? 'instant' : 'smooth'});
  }
  previous.addEventListener('click', () => go(current - 1));
  next.addEventListener('click', () => go(current + 1));
  thumbs.forEach((thumb, index) => thumb.addEventListener('click', () => go(index)));
  function restartAutoplay() {
    clearTimeout(timer);
    status.setAttribute('aria-live', 'polite');
    if (!inView || document.hidden || reduced.matches || slides.length < 2) return;
    timer = setTimeout(advance, 3000);
  }
  function advance() {
    const nextIndex = (current + 1) % slides.length;
    status.setAttribute('aria-live', 'off');
    go(nextIndex, nextIndex === 0);
    timer = setTimeout(advance, 3000);
  }
  gallery.addEventListener('click', restartAutoplay);
  track.addEventListener('pointerdown', restartAutoplay);
  track.addEventListener('pointerup', restartAutoplay);
  track.addEventListener('pointercancel', restartAutoplay);
  document.addEventListener('visibilitychange', restartAutoplay);
  reduced.addEventListener('change', restartAutoplay);
  new IntersectionObserver(([entry]) => {
    inView = entry.intersectionRatio >= .25;
    restartAutoplay();
  }, { threshold: .25 }).observe(track);
  track.addEventListener('scroll', () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(update); }, {passive:true});
  track.addEventListener('keydown', event => {
    if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
    event.preventDefault();
    restartAutoplay();
    go(event.key === 'Home' ? 0 : event.key === 'End' ? slides.length - 1 : current + (event.key === 'ArrowRight' ? 1 : -1));
  });
  new ResizeObserver(() => { track.scrollTo({left:current * track.clientWidth, behavior:'instant'}); update(); }).observe(track);
  update();
})();
