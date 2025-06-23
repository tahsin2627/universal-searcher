document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');

    // This is the CORRECT address for your working Render backend
    const BACKEND_URL = "https://universal-searcher-backend.onrender.com";

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            findResults(query);
        }
    });

    async function findResults(query) {
        resultsContainer.innerHTML = `<p class="no-results">Searching...</p>`;
        try {
            // This now calls your live Render backend
            const response = await fetch(`<span class="math-inline">\{BACKEND\_URL\}/search?q\=</span>{encodeURIComponent(query)}`);

            if (!response.ok) {
                displayResults(null); // Handles 404 "Not Found" and other errors
                return;
            }
            const result = await response.json();
            displayResults(result);
        } catch (error) {
            console.error('Search failed:', error);
            resultsContainer.innerHTML = `<p class="no-results">An error occurred. Please try again.</p>`;
        }
    }

    function displayResults(result) {
        resultsContainer.innerHTML = '';
        if (!result || !result.links || result.links.length === 0) {
            resultsContainer.innerHTML = `<p class="no-results">No results found.</p>`;
            return;
        }
        const resultItem = document.createElement('div');
        resultItem.classList.add('result-item');
        const titleElement = document.createElement('h2');
        titleElement.textContent = result.title;
        resultItem.appendChild(titleElement);
        result.links.forEach(link => {
            const linkElement = document.createElement('a');
            linkElement.href = link;
            linkElement.textContent = link;
            linkElement.target = '_blank';
            resultItem.appendChild(linkElement);
        });
        resultsContainer.appendChild(resultItem);
    }
});
