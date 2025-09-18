document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const webcamElement = document.getElementById('webcam');
    const canvasElement = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture-btn');
    const tryAgainBtn = document.getElementById('try-again-btn');

    const captureView = document.getElementById('capture-view');
    const loadingView = document.getElementById('loading-view');
    const resultsView = document.getElementById('results-view');

    const skinTypeResult = document.getElementById('skin-type-result');
    const recommendationsContainer = document.getElementById('recommendations-container');

    // SVG icons for product categories
    const icons = {
        cleanser: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>`,
        serum: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></svg>`,
        moisturizer: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>`,
        sunscreen: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`
    };
    
    // Helper function to create a delay
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // --- Webcam Setup ---
    async function setupWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            webcamElement.srcObject = stream;
            await webcamElement.play();
        } catch (err) {
            console.error("Error accessing webcam:", err);
            alert("Could not access webcam. Please ensure you have a webcam and have granted permission.");
        }
    }

    // --- Event Listeners ---
    captureBtn.addEventListener('click', captureAndAnalyze);
    tryAgainBtn.addEventListener('click', () => {
        showView('capture');
    });

    // --- Core Functions ---
    async function captureAndAnalyze() {
        // 1. Show loading state immediately
        showView('loading');

        // 2. Capture frame from webcam to canvas
        const context = canvasElement.getContext('2d');
        canvasElement.width = webcamElement.videoWidth;
        canvasElement.height = webcamElement.videoHeight;
        
        context.translate(webcamElement.videoWidth, 0);
        context.scale(-1, 1);
        context.drawImage(webcamElement, 0, 0, webcamElement.videoWidth, webcamElement.videoHeight);
        
        context.setTransform(1, 0, 0, 1, 0, 0); // Reset transform for future draws

        // 3. Convert canvas to a blob for sending
        canvasElement.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('image', blob, 'skin_capture.jpg');

            try {
                // 4. Create two promises: one for the server request, and one for our 2-second delay.
                const fetchPromise = fetch('/predict', { method: 'POST', body: formData });
                const delayPromise = sleep(2000); // 2000 milliseconds = 2 seconds

                // 5. Use Promise.all to wait for BOTH promises to complete.
                // This ensures the loading screen lasts at least 2 seconds.
                const [response] = await Promise.all([fetchPromise, delayPromise]);

                if (!response.ok) {
                    throw new Error(`Server error: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                // 6. Display results only after the server has responded AND 2 seconds have passed.
                displayResults(data);
                showView('results');

            } catch (error) {
                console.error('Error during analysis:', error);
                alert('An error occurred during analysis. Please try again.');
                showView('capture');
            }
        }, 'image/jpeg');
    }

    function displayResults(data) {
        skinTypeResult.textContent = data.skin_type || 'Unknown';
        recommendationsContainer.innerHTML = '';

        const products = data.recommendations;
        let delay = 0;

        for (const category in products) {
            const product = products[category];
            const card = document.createElement('div');
            card.className = 'product-card';
            card.style.animationDelay = `${delay}s`;

            const categoryTitle = category.charAt(0).toUpperCase() + category.slice(1);
            const iconHTML = `<div class="product-icon">${icons[category] || ''}</div>`;

            card.innerHTML = `
                <h3>${iconHTML} ${product.name}</h3>
                <p><strong>${categoryTitle}:</strong> ${product.description}</p>
            `;
            recommendationsContainer.appendChild(card);
            delay += 0.1; // Stagger animation for each card
        }
    }
    
    function showView(viewName) {
        captureView.classList.add('hidden');
        loadingView.classList.add('hidden');
        resultsView.classList.add('hidden');

        const viewToShow = document.getElementById(`${viewName}-view`);
        if(viewToShow) {
            viewToShow.classList.remove('hidden');
        }
    }

    // --- Initialization ---
    setupWebcam();
});

