/* 04 How it works: scroll-linked lettering, fallback only.
   Browsers with scroll-driven animations use css/how-marquee.css and this exits.
   Same mapping as the CSS: progress 0 when the band's top meets the viewport bottom,
   1 when its bottom leaves the viewport top; translateX = -progress * travel. */
(() => {
  const track = document.querySelector('.how-marquee__track');
  if (!track || (window.CSS && CSS.supports('animation-timeline: view()'))) return;
  const band = track.parentElement;
  const calm = matchMedia('(prefers-reduced-motion: reduce)');
  const travel = () => Math.min(380, Math.max(200, innerWidth * .26));   // clamp(200px, 26vw, 380px)
  let frame = 0;
  let near = false;

  function paint() {
    frame = 0;
    if (calm.matches) { track.style.transform = ''; return; }
    const r = band.getBoundingClientRect();
    const p = Math.min(1, Math.max(0, (innerHeight - r.top) / (innerHeight + r.height)));
    track.style.transform = `translate3d(${(-p * travel()).toFixed(2)}px, 0, 0)`;
  }
  const request = () => { if (!frame) frame = requestAnimationFrame(paint); };

  new IntersectionObserver(([entry]) => { near = entry.isIntersecting; request(); },
    {rootMargin: '120px 0px'}).observe(band);
  addEventListener('scroll', () => { if (near) request(); }, {passive: true});
  addEventListener('resize', request, {passive: true});
  if (calm.addEventListener) calm.addEventListener('change', request);
  paint();
})();
