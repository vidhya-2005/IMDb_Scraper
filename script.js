let allMovies = [];

async function startScrape() {
    const btn = document.getElementById("scrapeBtn");
    const status = document.getElementById("status");
    
    btn.disabled = true;
    status.textContent = "Scraping...";
    
    try {
        const response = await fetch('/scrape');
        allMovies = await response.json();

        if (allMovies.length === 0) {
            status.textContent = "Failed. Check Python console.";
            status.style.color = "red";
        } else {
            status.textContent = `Loaded ${allMovies.length} movies.`;
            status.style.color = "green";
            applyFilters(); 
        }
    } catch (error) {
        console.error(error);
        status.textContent = "Server Error.";
    } finally {
        btn.disabled = false;
    }
}

function applyFilters() {
    const sortValue = document.getElementById("sortSelect").value;
    const genreFilter = document.getElementById("genreFilter").value;
    const tbody = document.querySelector("#movieTable tbody");

    // 1. FILTER
    let filtered = allMovies.filter(movie => {
        if (genreFilter === "all") return true;
        return movie.Genres.some(g => g.includes(genreFilter));
    });

    // 2. SORT
    filtered.sort((a, b) => {
        if (sortValue === "rating_high") return b.Rating - a.Rating;
        if (sortValue === "rating_low") return a.Rating - b.Rating;
        if (sortValue === "date_new") return b.Year - a.Year;
        if (sortValue === "date_old") return a.Year - b.Year;
    });

    // 3. RENDER TABLE ROWS
    tbody.innerHTML = "";
    
    if (filtered.length === 0) {
        tbody.innerHTML = "<tr><td colspan='5' style='text-align:center;'>No movies found.</td></tr>";
        return;
    }

    filtered.forEach(movie => {
        const genreBadges = movie.Genres.slice(0, 3).map(g => 
            `<span class="badge-genre">${g}</span>`
        ).join("");

        const row = document.createElement("tr");
        row.innerHTML = `
            <td class="rank-cell">#${movie.Rank}</td>
            <td style="font-weight:bold; color:#000;">${movie.Title}</td>
            <td>${genreBadges}</td>
            <td>${movie.Year}</td>
            <td class="rating-cell">⭐ ${movie.Rating}</td>
        `;
        tbody.appendChild(row);
    });
}
