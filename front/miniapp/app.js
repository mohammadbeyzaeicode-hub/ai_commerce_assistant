
function getTelegramWebApp() {
  // بررسی صحیح وجود Telegram
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp;
  }
  return null;
}

const statusText = document.getElementById('status-text');
const closeButton = document.getElementById('close-app');
const productsList = document.getElementById('products-list');
const productsState = document.getElementById('products-state');
const stateTitle = document.getElementById('state-title');
const stateMessage = document.getElementById('state-message');
const retryButton = document.getElementById('retry-products');

const productsEndpoint =
  `${window.APP_CONFIG.API_BASE_URL}/api/v1/products/`;

const queryParams = new URLSearchParams(window.location.search);
const botToken = queryParams.get('bot_token');

const numberFormatter = new Intl.NumberFormat('fa-IR');


function getTelegramStatus(telegram = getTelegramWebApp()) {
  return {
    hasWebApp: Boolean(telegram),
    hasInitData: Boolean(telegram?.initData),
    initDataLength: telegram?.initData?.length ?? 0,
    hasUser: Boolean(telegram?.initDataUnsafe?.user),
    platform: telegram?.platform ?? 'unknown',
    version: telegram?.version ?? 'unknown',
    hasBotToken: Boolean(botToken),
  };
}


function showDiagnostic(message) {
  const diagnostic = document.getElementById('diagnostic');
  if (diagnostic) {
    diagnostic.hidden = false;
    diagnostic.textContent = message;
  }
  console.log('📊 Diagnostic:', message);
}


async function waitForTelegramInitData(timeoutMs = 5000) {
  const startedAt = Date.now();
  let lastTelegram = null;

  while (Date.now() - startedAt < timeoutMs) {
    const telegram = getTelegramWebApp();
    lastTelegram = telegram;

    if (telegram?.initData) {
      console.log('✅ Telegram initData loaded');
      return telegram;
    }

    // اگر Telegram موجود است اما initData ندارد، بیشتر صبر کن
    if (telegram && !telegram.initData) {
      console.log('⏳ Waiting for Telegram initData...');
    }

    await new Promise((resolve) => setTimeout(resolve, 200));
  }

  console.warn('⚠️ Timeout waiting for Telegram initData');
  return lastTelegram;
}


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

  if (
    typeof product.image_url === 'string' &&
    product.image_url
  ) {
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
  description.textContent =
    product.description ||
    'توضیحی برای این محصول ثبت نشده است.';

  const footer = document.createElement('div');
  footer.className = 'product-footer';

  const price = document.createElement('strong');
  price.textContent =
    `${numberFormatter.format(product.price)} تومان`;

  const availability = document.createElement('span');

  availability.className =
    product.is_active && product.inventory > 0
      ? 'inventory available'
      : 'inventory unavailable';

  availability.textContent =
    product.is_active && product.inventory > 0
      ? `موجودی: ${numberFormatter.format(product.inventory)}`
      : 'ناموجود';

  footer.append(price, availability);

  info.append(name, description, footer);

  card.append(imageArea, info);


  card.addEventListener('click', () => {
    handleProductClick(product);
  });


  card.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleProductClick(product);
    }
  });


  return card;
}


function handleProductClick(product) {
  console.info(
    'Product selected; details page is not implemented yet.',
    product.id
  );
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

  productsList.innerHTML =
    '<div class="skeleton-card" aria-hidden="true">' +
      '<div class="skeleton-image"></div>' +
      '<div class="skeleton-lines">' +
        '<span></span>' +
        '<span></span>' +
        '<span></span>' +
      '</div>' +
    '</div>'.repeat(3);

  console.log('🔍 Debug Info:');
  console.log('   productsEndpoint:', productsEndpoint);
  console.log('   botToken:', botToken);

  // مهم:
  // telegram را بیرون try تعریف می‌کنیم
  // تا داخل catch هم به آن دسترسی داشته باشیم.
  let telegram = null;


  try {

    telegram = await waitForTelegramInitData();

    // اطلاعات تشخیصی اولیه
    const status = getTelegramStatus(telegram);

    console.log('📊 Telegram Status:', status);

    if (!telegram) {
      throw new Error(
        '❌ Telegram WebApp is unavailable. Open this page from Telegram.'
      );
    }


    if (!telegram.initData) {
      console.warn('⚠️ initData is empty. Possible causes:\n' +
        '1. Page opened directly (not as Telegram Web App)\n' +
        '2. Bot token missing from URL\n' +
        '3. Telegram script not fully loaded');
      
      throw new Error(
        `❌ Telegram init data is missing. ` +
        `This app must be opened from Telegram using the Web App button. ` +
        `botToken=${status.hasBotToken}`
      );
    }


    if (!botToken) {
      throw new Error(
        'Bot token is missing from the mini-app URL. ' +
        'Restart the bot and open a newly generated menu.'
      );
    }

    console.log('✅ All validations passed. Fetching products...');

    // درخواست محصولات
    const response = await fetch(productsEndpoint, {
      headers: {
        'X-Telegram-Init-Data': telegram.initData,
        'X-Telegram-Bot-Token': botToken,
      },
    });

    console.log('📡 API Response Status:', response.status);

    if (!response.ok) {
      let detail = '';

      try {
        const body = await response.json();
        console.log('❌ API Error Response:', body);

        detail = body.detail
          ? `: ${body.detail}`
          : '';
      } catch {
        // API ممکن است پاسخ JSON نداشته باشد.
      }

      throw new Error(
        `Products request failed: ${response.status}${detail}`
      );
    }


    const products = await response.json();
    console.log('✅ Products loaded:', products.length);

    productsList.replaceChildren(
      ...products.map(productCard)
    );

    productsList.setAttribute('aria-busy', 'false');


    if (!products.length) {
      showState(
        'محصولی پیدا نشد',
        'در حال حاضر محصولی برای نمایش وجود ندارد.'
      );
    }


  } catch (error) {

    productsList.replaceChildren();

    productsList.setAttribute('aria-busy', 'false');

    console.error('❌ Error:', error);

    showState(
      'دریافت محصولات انجام نشد',
      'اتصال به فروشگاه برقرار نشد. دوباره تلاش کنید.',
      true
    );

  } finally {

    retryButton.disabled = false;

  }
}


// -------------------------
// Telegram initialization
// -------------------------

const telegram = getTelegramWebApp();


if (telegram) {

  telegram.ready();
  telegram.expand();

  statusText.textContent =
    telegram.initData
      ? 'متصل به تلگرام'
      : 'حالت آزمایشی مرورگر';

} else {

  statusText.textContent =
    'حالت آزمایشی مرورگر';

}


// -------------------------
// Close button
// -------------------------

closeButton.addEventListener('click', () => {

  const telegram = getTelegramWebApp();

  if (telegram) {
    telegram.close();
  } else {
    window.history.back();
  }

});


// -------------------------
// Retry
// -------------------------

retryButton.addEventListener(
  'click',
  loadProducts
);


// -------------------------
// Initial load
// -------------------------

loadProducts();
