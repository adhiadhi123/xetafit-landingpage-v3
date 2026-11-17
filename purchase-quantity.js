(() => {
  const selector = document.querySelector('[data-pack-quantity]');
  if (!selector) return;
  const value = selector.querySelector('output');
  const summary = selector.querySelector('[data-quantity-summary]');
  const buttons = [...selector.querySelectorAll('[data-quantity-step]')];
  let quantity = 1;
  buttons.forEach(button => button.addEventListener('click', () => {
    quantity = Math.max(1, Math.min(Math.floor(Number.MAX_SAFE_INTEGER / 60), quantity + Number(button.dataset.quantityStep)));
    value.value = String(quantity);
    summary.textContent = `${quantity} ${quantity === 1 ? 'Pack' : 'Packs'} of 4 = ${quantity * 4} tubes = ${quantity * 60} tablets.`;
    buttons.find(b => b.dataset.quantityStep === '-1').disabled = quantity === 1;
  }));
})();
