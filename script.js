// File: script.js (Final Version)

document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent page from reloading
        const query = searchInput.value.trim();
        if (query) {
            findResults(query);
        }
    });

    async function findResults(query) {
        // Clear previous results and show a loading message
        resultsContainer.innerHTML = `<p class="no-results">Searching...</p>`;

        try {
            // --- THIS IS THE NEW PART ---
            // We now call our live Netlify Function API
            const response = await fetch(`/.netlify/functions/search?q=${query}`);

            // If the API returns a "not found" error, show that message
            if (response.status === 404) {
                displayResults(null); // Passing null will trigger the "No results found" message
                return;
            }

            // If the response is not ok for any other reason, throw an error
            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }
            
            const result = await response.json();
            displayResults(result);
            // --- END OF NEW PART ---

        } catch (error) {
            console.error('Search failed:', error);
            resultsContainer.innerHTML = `<p class="no-results">An error occurred. Please try again.</p>`;
        }
    }

    function displayResults(result) {
        // Clear the "Searching..." message
        resultsContainer.innerHTML = '';

        if (!result) {
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
            linkElement.target = '_blank'; // Open link in a new tab
            resultItem.appendChild(linkElement);
        });

        resultsContainer.appendChild(resultItem);
    }
});
