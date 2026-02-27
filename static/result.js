const params = new URLSearchParams(window.location.search);
const query = params.get('q')

if(query){
    document.querySelector('.results-heading').textContent = `Results for "${query}"`;

    fetch(`/search?q=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
        if(data.error){
            document.querySelector('#results').innerHTML = `<p class="error">${data.error}</p>`
        } else {
            displayResults(data);
            fetch('/wishlist/items')
            .then(res => res.json())
            .then(wishlistedUrls => {
                document.querySelectorAll('.wishlist-btn').forEach(btn => {
                    if(wishlistedUrls.includes(btn.dataset.url)){
                        btn.classList.add('active')
                    }
                })
            })
        }
    })
    .catch(err => {
        console.error('Fetch error:', err);
        document.querySelector('#results').innerHTML = `<p class="error">Something went wrong.</p>`;
    });

} else {
    document.querySelector('#results').innerHTML = `<p class="error">No search query provided.</p>`;
}


function displayResults(results){
    const container = document.querySelector('#results')
    container.innerHTML = "";

    results.forEach(product => {
        const ratingClass = product.rating === "N/A" ? "rating-badge no-rating" : "rating-badge";
        const productHTML = `
            <div class="product-item">
                <img 
                    class="product-image" 
                    src="${product.image !== "N/A" ? product.image : "https://via.placeholder.com/200"}"
                >
                <div class="product-details">
                    <div class="product-title">${product.name}</div>
                    <div class="product-actions">
                        <div class="${ratingClass}">
                            ${product.rating !== "N/A" ? product.rating + " ★" : "No Rating"}
                        </div>
                        <div class="price">${product.price}</div>
                        <button class="wishlist-btn"
                            data-name="${product.name}"
                            data-price="${product.price}"
                            data-image="${product.image}"
                            data-url="${product.url}"
                            onclick="toggleWishlist(this)">
                            <svg viewBox="0 0 24 24" width="24" height="24">
                                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += productHTML;
    })
}

function toggleWishlist(btn){
    fetch('/check-login')
    .then(res => res.json())
    .then(data => {
        if(!data.logged_in){
            window.location.href = '/login'
            return
        }

        btn.classList.toggle('active')
        const targetPrice = prompt('Enter target price (optional)')
        fetch('/wishlist/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name: btn.dataset.name,
                price: btn.dataset.price,
                image: btn.dataset.image,
                url: btn.dataset.url,
                target_price: targetPrice
            })
        })
        .then(res => res.json())
        .then(data => console.log(data))
        .catch(err => console.log(err))
    })
}