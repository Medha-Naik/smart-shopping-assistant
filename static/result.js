const params = new URLSearchParams(window.location.search);
const query = params.get('q');
let allResults = [];

if (query) {
  fetch(`/search?q=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        document.querySelector('#results').innerHTML = `<p class="error">${data.error}</p>`;
      } else {
        allResults = data;
        sortResults('asc');
  
        fetch('/wishlist/items')
          .then(res => res.json())
          .then(wishlistedUrls => {
            document.querySelectorAll('.wishlist-btn').forEach(btn => {
              if (wishlistedUrls.includes(btn.dataset.url)) btn.classList.add('active');
            });
          })
          .catch(() => {});
      }
    })
    .catch(() => {
      document.querySelector('#results').innerHTML = `<p class="error">Something went wrong. Please try again.</p>`;
    });
} else {
  document.querySelector('#results').innerHTML = `<p class="error">No search query provided.</p>`;
}

function parsePrice(item) {
  const raw = item.price || '';
  const nums = raw.replace(/[^\d]/g, '');
  return nums ? parseInt(nums) : 999999999;
}

function sortResults(order) {


  const sorted = [...allResults];
  if (order === 'asc') sorted.sort((a, b) => parsePrice(a) - parsePrice(b));
  else if (order === 'desc') sorted.sort((a, b) => parsePrice(b) - parsePrice(a));
  else if (order === 'flipkart') sorted.sort((a, b) => (a.source === 'Flipkart' ? -1 : 1));
  else if (order === 'girias') sorted.sort((a, b) => (a.source === 'Girias' ? -1 : 1));
  displayResults(sorted);

  // Re-highlight wishlisted items
  fetch('/wishlist/items')
    .then(res => res.json())
    .then(wishlistedUrls => {
      document.querySelectorAll('.wishlist-btn').forEach(btn => {
        if (wishlistedUrls.includes(btn.dataset.url)) btn.classList.add('active');
      });
    })
    .catch(() => {});
}

function displayResults(results) {
  const container = document.querySelector('#results');
  container.innerHTML = '';

  results.forEach(product => {
    const ratingClass = product.rating === 'N/A' ? 'rating-badge no-rating' : 'rating-badge';
    const ratingText = product.rating !== 'N/A' ? `${product.rating} ★` : 'No rating';
    const imgSrc = product.image && product.image !== 'N/A'
      ? product.image
      : 'https://via.placeholder.com/200x200/111111/333333?text=No+Image';
    const source = product.source || 'Flipkart';
    const sourceColor = source === 'Girias' ? '#c8a97e' : '#6fb3ff';

    container.innerHTML += `
      <div class="product-item">
        <div class="product-image-wrap">
          <img class="product-image" src="${imgSrc}" alt="${product.name}" loading="lazy">
        </div>
        <div class="product-details">
          <span style="font-size:11px;font-weight:500;letter-spacing:0.06em;color:${sourceColor};text-transform:uppercase;">${source}</span>
          <div class="product-title">${product.name}</div>
          <div class="price">${product.price}</div>
          <div class="product-meta">
            <span class="${ratingClass}">${ratingText}</span>
            <button class="wishlist-btn"
              data-name="${product.name}"
              data-price="${product.price}"
              data-image="${product.image}"
              data-url="${product.url}"
              onclick="toggleWishlist(this)"
              title="Add to wishlist">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
  });
}

function toggleWishlist(btn) {
  fetch('/check-login')
    .then(res => res.json())
    .then(data => {
      if (!data.logged_in) { window.location.href = '/login'; return; }
      btn.classList.toggle('active');
      const targetPriceInput = prompt('Set a target price (leave blank to skip)');
      const targetPrice = targetPriceInput ? targetPriceInput.trim() : null;
      fetch('/wishlist/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: btn.dataset.name,
          price: btn.dataset.price,
          image: btn.dataset.image,
          url: btn.dataset.url,
          target_price: targetPrice
        })
      }).then(r => r.json()).catch(console.error);
    });
}