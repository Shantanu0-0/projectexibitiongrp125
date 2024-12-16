// URLs for the backend API
const API_URL_PROCESS = "http://127.0.0.1:5000/process";

// Handle Selection Form Submission
document.getElementById("selection-form").addEventListener("submit", (event) => {
    event.preventDefault();

    // Show routes section
    document.getElementById("selection-section").style.display = "none";
    document.getElementById("routes-section").style.display = "block";
});

// Handle Routes Form Submission
document.getElementById("routes-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    // Get selected routes
    const selectedRoutes = Array.from(document.querySelectorAll("input[name='route']:checked"))
        .map(input => input.value);

    if (selectedRoutes.length < 1) {
        alert("Please select at least one route.");
        return;
    }

    // Map selected routes to actual video file paths
    const videoPaths = selectedRoutes.map(route => {
        if (route === "route-1") return "C:/Users/USER/cand video 1.mp4";
        if (route === "route-2") return "C:/Users/USER/cand video 2.mp4";
        if (route === "route-3") return "C:/Users/USER/cand video 3.mp4";
        if (route === "route-4") return "C:/Users/USER/cand video 4.mp4";
    });

    // Show loading section
    document.getElementById("routes-section").style.display = "none";
    document.getElementById("loading-section").style.display = "block";

    try {
        // Send request to backend with actual video paths
        const response = await fetch(API_URL_PROCESS, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ video_paths: videoPaths })
        });

        if (!response.ok) {
            throw new Error("Error processing request");
        }

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        alert("An error occurred: " + error.message);
    } finally {
        // Hide loading section
        document.getElementById("loading-section").style.display = "none";
    }
});

// Display Results
function displayResults(data) {
    const resultsContainer = document.getElementById("results-container");
    resultsContainer.innerHTML = "";

    if (data.road_scores) {
        data.road_scores.forEach((road) => {
            const roadDiv = document.createElement("div");
            roadDiv.classList.add("road-result");
            roadDiv.innerHTML = `
                <h3>Route ${road.road_id}</h3>
                <p>Score: ${road.score.toFixed(2)}</p>
                <p>Average Road Width: ${road.metrics.road_width.toFixed(2)}</p>
                <p>Average Traffic Count: ${road.metrics.traffic_count.toFixed(2)}</p>
                <p>Average Speed: ${road.metrics.speed.toFixed(2)}</p>
                <p>Average Density: ${road.metrics.density.toFixed(2)}</p>
            `;
            resultsContainer.appendChild(roadDiv);
        });

        // Highlight the best and worst routes
        const bestRoute = data.best_road;
        const worstRoute = data.worst_road;

        if (bestRoute) {
            resultsContainer.innerHTML += `<h3>Best Route: Route ${bestRoute.road_id}</h3>`;
        }
        if (worstRoute) {
            resultsContainer.innerHTML += `<h3>Worst Route: Route ${worstRoute.road_id}</h3>`;
        }
    } else {
        resultsContainer.innerHTML = "<p>No data available.</p>";
    }

    // Show results section
    document.getElementById("results-section").style.display = "block";
}
