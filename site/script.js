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

const galleryImages = document.querySelectorAll('.gallery-grid .gallery-item img');

if (galleryImages.length > 0) {
  const lightbox = document.createElement('div');
  lightbox.className = 'gallery-lightbox';
  lightbox.setAttribute('aria-hidden', 'true');

  const closeButton = document.createElement('button');
  closeButton.className = 'gallery-lightbox-close';
  closeButton.type = 'button';
  closeButton.setAttribute('aria-label', 'Close enlarged image');
  closeButton.textContent = '×';

  const lightboxImage = document.createElement('img');
  lightboxImage.className = 'gallery-lightbox-image';
  lightboxImage.alt = '';

  lightbox.append(closeButton, lightboxImage);
  document.body.append(lightbox);

  const closeLightbox = () => {
    lightbox.classList.remove('is-open');
    lightbox.setAttribute('aria-hidden', 'true');
    lightboxImage.removeAttribute('src');
  };

  const openLightbox = (image) => {
    lightboxImage.src = image.src;
    lightboxImage.alt = image.alt;
    lightbox.classList.add('is-open');
    lightbox.setAttribute('aria-hidden', 'false');
  };

  galleryImages.forEach((image) => {
    image.addEventListener('click', () => openLightbox(image));
  });

  closeButton.addEventListener('click', closeLightbox);

  lightbox.addEventListener('click', (event) => {
    if (event.target === lightbox) {
      closeLightbox();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && lightbox.classList.contains('is-open')) {
      closeLightbox();
    }
  });
}
