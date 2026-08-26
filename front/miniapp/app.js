const telegram = window.Telegram?.WebApp;
const statusText = document.getElementById('status-text');
const closeButton = document.getElementById('close-app');
const productsList = document.getElementById('products-list');
const productsState = document.getElementById('products-state');
const stateTitle = document.getElementById('state-title');
const stateMessage = document.getElementById('state-message');
const retryButton = document.getElementById('retry-products');
// const productsEndpoint = 'https://fair-democrat-horizontal-secret.trycloudflare.com/api/v1/products/';
const productsEndpoint = `${window.APP_CONFIG.API_BASE_URL}/api/v1/products/`;

const numberFormatter = new Intl.NumberFormat('fa-IR');

function productCard(product) {
  const card = document.createElement('article');
  card.className = 'product-card';
  card.tabIndex = 0;
  card.setAttribute('role', 'button');
  card.setAttribute('aria-label', `مشاهده ${product.name}`);

  const imageArea = document.createElement('div');
  imageArea.className = 'product-image';
  const imageLabel = document.createElement('span');
  imageLabel.className = 'image-label';
  imageLabel.textContent = 'تصویر محصول';
  if (typeof product.image_url === 'string' && product.image_url) {
    const image = document.createElement('img');
    image.src = product.image_url;
    image.alt = product.name;
    imageArea.append(image);
  } else {
    const imageMark = document.createElement('span');
    imageMark.className = 'image-mark';
    imageMark.setAttribute('aria-hidden', 'true');
    imageMark.textContent = '✦';
    imageArea.append(imageMark);
  }
  imageArea.append(imageLabel);

  const info = document.createElement('div');
  info.className = 'product-info';
  const name = document.createElement('h3');
  name.textContent = product.name;
  const description = document.createElement('p');
  description.className = 'product-description';
  description.textContent = product.description || 'توضیحی برای این محصول ثبت نشده است.';
  const footer = document.createElement('div');
  footer.className = 'product-footer';
  const price = document.createElement('strong');
  price.textContent = `${numberFormatter.format(product.price)} تومان`;
  const availability = document.createElement('span');
  availability.className = product.is_active && product.inventory > 0 ? 'inventory available' : 'inventory unavailable';
  availability.textContent = product.is_active && product.inventory > 0
    ? `موجودی: ${numberFormatter.format(product.inventory)}`
    : 'ناموجود';
  footer.append(price, availability);
  info.append(name, description, footer);
  card.append(imageArea, info);
  card.addEventListener('click', () => handleProductClick(product));
  card.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleProductClick(product);
    }
  });
  return card;
}

function handleProductClick(product) {
  console.info('Product selected; details page is not implemented yet.', product.id);
}

function showState(title, message, canRetry = false) {
  stateTitle.textContent = title;
  stateMessage.textContent = message;
  retryButton.hidden = !canRetry;
  productsState.hidden = false;
}

async function loadProducts() {
  retryButton.disabled = true;
  productsList.setAttribute('aria-busy', 'true');
  productsState.hidden = true;
  productsList.innerHTML = '<div class="skeleton-card" aria-hidden="true"><div class="skeleton-image"></div><div class="skeleton-lines"><span></span><span></span><span></span></div></div>'.repeat(3);

  try {
    const response = await fetch(productsEndpoint);
    if (!response.ok) throw new Error(`Products request failed: ${response.status}`);

    const products = await response.json();
    productsList.replaceChildren(...products.map(productCard));
    productsList.setAttribute('aria-busy', 'false');
    if (!products.length) showState('محصولی پیدا نشد', 'در حال حاضر محصولی برای نمایش وجود ندارد.');
  } catch (error) {
    productsList.replaceChildren();
    productsList.setAttribute('aria-busy', 'false');
    showState('دریافت محصولات انجام نشد', 'اتصال به فروشگاه برقرار نشد. دوباره تلاش کنید.', true);
    console.error(error);
  } finally {
    retryButton.disabled = false;
  }
}

if (telegram) {
  telegram.ready();
  telegram.expand();
  statusText.textContent = telegram.initData ? 'متصل به تلگرام' : 'حالت آزمایشی مرورگر';
} else {
  statusText.textContent = 'حالت آزمایشی مرورگر';
}

closeButton.addEventListener('click', () => {
  if (telegram) telegram.close();
  else window.history.back();
});

retryButton.addEventListener('click', loadProducts);
loadProducts();
