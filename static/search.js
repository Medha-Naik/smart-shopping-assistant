const params = new URLSearchParams(window.location.search)
const query = params.get('q')

fetch(`/search?q=${query}`)
    .then(res => res.json())
    .then(results => displayResults(results))

function displayResults(results) {
    const container = document.querySelector('#results')

    results.forEach(product => {
        const card = `
            <div class="product-card">
                <img src="${product.image}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p>Amazon: ₹${product.prices[0].price}</p>
                <p>Flipkart: ₹${product.prices[1].price}</p>
                <button>Add to Wishlist</button>
            </div>
        `
        container.innerHTML += card
    })
}
