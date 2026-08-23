const telegram = window.Telegram?.WebApp;
const status = document.getElementById('telegram-status');
const closeButton = document.getElementById('close-app');

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
