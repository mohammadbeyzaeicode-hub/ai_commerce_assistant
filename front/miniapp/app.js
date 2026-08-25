const telegram = window.Telegram?.WebApp;
const status = document.getElementById('telegram-status');
const closeButton = document.getElementById('close-app');
const loadProductsButton = document.getElementById('load-products');
const productsList = document.getElementById('products-list');
const productsMessage = document.getElementById('products-message');
const productsEndpoint = 'https://fair-democrat-horizontal-secret.trycloudflare.com/api/v1/products/';

const numberFormatter = new Intl.NumberFormat('fa-IR');

function productCard(product) {
  const card = document.createElement('article');
  card.className = 'product-card';
  card.innerHTML = `
    <div class="product-art" aria-hidden="true">
      <span class="art-label">${product.is_active ? 'موجود' : 'غیرفعال'}</span>
      <div class="product-shape"></div>
    </div>
    <div class="product-info">
      <div>
        <p class="product-category">شناسه محصول: ${numberFormatter.format(product.id)}</p>
        <h3></h3>
      </div>
      <p class="product-description"></p>
      <div class="product-footer">
        <strong>${numberFormatter.format(product.price)} تومان</strong>
        <span class="inventory">موجودی: ${numberFormatter.format(product.inventory)}</span>
      </div>
    </div>`;
  card.querySelector('h3').textContent = product.name;
  card.querySelector('.product-description').textContent = product.description || 'توضیحی برای این محصول ثبت نشده است.';
  return card;
}

async function loadProducts() {
  loadProductsButton.disabled = true;
  loadProductsButton.textContent = 'در حال دریافت...';
  productsMessage.textContent = 'در حال دریافت محصولات...';

  try {
    const response = await fetch(productsEndpoint);
    console.log('Products response:', response);
    if (!response.ok) throw new Error(`Products request failed: ${response.status}`);

    const products = await response.json();
    productsList.replaceChildren(...products.map(productCard));
    productsMessage.textContent = products.length
      ? `${numberFormatter.format(products.length)} محصول دریافت شد.`
      : 'محصولی برای نمایش وجود ندارد.';
  } catch (error) {
    productsMessage.textContent = 'دریافت محصولات انجام نشد. اتصال API را بررسی کنید.';
    productsList.replaceChildren();
    console.error(error);
  } finally {
    loadProductsButton.disabled = false;
    loadProductsButton.textContent = 'دریافت محصولات';
  }
}

if (telegram) {
  telegram.ready();
  telegram.expand();
  status.textContent = telegram.initData ? 'متصل به تلگرام' : 'صفحه در حالت تست مرورگر';
  telegram.MainButton.setText('ادامه خرید').hide();
} else {
  status.textContent = 'صفحه در حالت تست مرورگر';
}

closeButton.addEventListener('click', () => {
  if (telegram) telegram.close();
  else window.history.back();
});

loadProductsButton.addEventListener('click', loadProducts);
