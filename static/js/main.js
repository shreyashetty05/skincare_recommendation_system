// document.addEventListener('DOMContentLoaded', () => {
//     // --- Elements ---
//     const analysisView = document.getElementById('analysis-view');
//     const captureView = document.getElementById('capture-view');
//     const loadingView = document.getElementById('loading-view');
//     const resultsView = document.getElementById('results-view');
//     const backToHomeBtn = document.querySelector('.back-button'); // Use querySelector for class
//     const captureBtn = document.getElementById('capture-btn');
//     const tryAgainBtn = document.getElementById('try-again-btn');
//     const webcamElement = document.getElementById('webcam');
//     const canvasElement = document.getElementById('canvas');
//     const skinTypeResult = document.getElementById('skin-type-result');
//     const recommendationsContainer = document.getElementById('recommendations-container');
//     const customAlert = document.getElementById('custom-alert');
//     const alertMessage = document.getElementById('alert-message');
//     const alertCloseBtn = document.getElementById('alert-close-btn');

//     // --- State & Icons ---
//     let webcamStream = null;
//     const icons = {
//         cleanser: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>`,
//         serum: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></svg>`,
//         moisturizer: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>`,
//         sunscreen: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`
//     };
    
//     // --- Custom Alert Logic ---
//     function showAlert(message) {
//         alertMessage.textContent = message;
//         customAlert.classList.add('show');
//         customAlert.classList.remove('hidden');
//     }
//     function hideAlert() {
//         customAlert.classList.remove('show');
//         customAlert.classList.add('hidden');
//     }

//     // --- Webcam Management ---
//     async function startWebcam() {
//         if (webcamStream) return;
//         try {
//             webcamStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
//             webcamElement.srcObject = webcamStream;
//             await webcamElement.play();
//         } catch (err) {
//             console.error("Error accessing webcam:", err);
//             showAlert("Could not access webcam. Please grant permission.");
//         }
//     }
//     function stopWebcam() {
//         if (webcamStream) {
//             webcamStream.getTracks().forEach(track => track.stop());
//             webcamStream = null;
//         }
//     }

//     // --- View Navigation ---
//     function showAnalysisSubView(subViewToShow) {
//         captureView.classList.add('hidden');
//         loadingView.classList.add('hidden');
//         resultsView.classList.add('hidden');
//         subViewToShow.classList.remove('hidden');
//     }

//     // --- Event Listeners ---
//     if(backToHomeBtn) {
//         backToHomeBtn.addEventListener('click', () => {
//             stopWebcam();
//             // This will navigate to the homepage route defined in Flask
//             window.location.href = '/';
//         });
//     }
//     tryAgainBtn.addEventListener('click', () => showAnalysisSubView(captureView));
//     captureBtn.addEventListener('click', captureAndAnalyze);
//     alertCloseBtn.addEventListener('click', hideAlert);

//     // --- Core Logic (Analysis) ---
//     function captureAndAnalyze() {
//         hideAlert();
//         showAnalysisSubView(loadingView);
//         const context = canvasElement.getContext('2d');
//         canvasElement.width = webcamElement.videoWidth;
//         canvasElement.height = webcamElement.videoHeight;
//         context.translate(webcamElement.videoWidth, 0);
//         context.scale(-1, 1);
//         context.drawImage(webcamElement, 0, 0, webcamElement.videoWidth, webcamElement.videoHeight);
//         context.setTransform(1, 0, 0, 1, 0, 0);

//         canvasElement.toBlob(async (blob) => {
//             const formData = new FormData();
//             formData.append('image', blob, 'skin_capture.jpg');
//             try {
//                 // The API call to the backend will have a natural delay while Gemini works
//                 const response = await fetch('/predict', { method: 'POST', body: formData });
//                 const data = await response.json();
                
//                 // Check if the server responded with an error
//                 if (!response.ok) {
//                     throw new Error(data.error || 'An unknown error occurred.');
//                 }
                
//                 displayResults(data);
//                 showAnalysisSubView(resultsView);
//             } catch (error) {
//                 console.error('Error during analysis:', error);
//                 showAlert(error.message); // Use our new custom alert
//                 showAnalysisSubView(captureView);
//             }
//         }, 'image/jpeg');
//     }

//     function displayResults(data) {
//         skinTypeResult.textContent = data.skin_type || 'Unknown';
//         recommendationsContainer.innerHTML = '';
//         let delay = 0;

//         for (const category in data.recommendations) {
//             const product = data.recommendations[category];
//             const card = document.createElement('div');
//             card.className = 'product-card';
//             card.style.animationDelay = `${delay}s`;

//             const categoryTitle = category.charAt(0).toUpperCase() + category.slice(1);
//             const iconHTML = `<div class="product-icon">${icons[category] || ''}</div>`;
            
//             // --- E-commerce Price Comparison Logic ---
//             let priceHTML = '<div class="price-container">';
//             if (product.prices && product.prices.length > 0) {
//                 product.prices.forEach(priceInfo => {
//                     priceHTML += `
//                         <div class="price-comparison-row">
//                             <span class="retailer-name">${priceInfo.retailer}</span>
//                             <span class="retailer-price">${priceInfo.price}</span>
//                             <a href="${priceInfo.url}" target="_blank" rel="noopener noreferrer" class="buy-button">Buy Now</a>
//                         </div>
//                     `;
//                 });
//             } else {
//                 priceHTML += '<p class="no-price-found">Could not fetch live prices.</p>';
//             }
//             priceHTML += '</div>';

//             card.innerHTML = `
//                 <h3>${iconHTML} ${product.name}</h3>
//                 <p><strong>${categoryTitle}:</strong> ${product.description}</p>
//                 ${priceHTML}
//             `;
//             recommendationsContainer.appendChild(card);
//             delay += 0.1;
//         }
//     }

//     // --- Initialization ---
//     startWebcam();
// });

