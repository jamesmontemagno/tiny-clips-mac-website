const year = document.getElementById('year');
if (year) {
  year.textContent = String(new Date().getFullYear());
}

const appStoreLink = document.getElementById('app-store-link');
if (appStoreLink) {
  appStoreLink.addEventListener('click', (event) => {
    event.preventDefault();
    appStoreLink.textContent = 'App Store (Not Live Yet)';
  });
}
