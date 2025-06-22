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

    function findResults(query) {
        // --- DUMMY DATA FOR TESTING ---
        // In the future, this will be replaced with a real API call to our backend.
        const mockDatabase = {
            "the dark knight": {
                title: "The Dark Knight",
                links: [
                    "https://vidsrc.to/embed/movie/tt0468569",
                    "https://archive.org/download/TheDarkKnight_201408/TheDarkKnight.mp4"
                ]
            }
        };
        
        const result = mockDatabase[query.toLowerCase()];
        displayResults(result);
        // --- END OF DUMMY DATA SECTION ---
    }

    function displayResults(result) {
        // Clear previous results
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
