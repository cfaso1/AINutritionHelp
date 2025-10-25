// ============================================================================
// BARCODE SCANNER FUNCTIONS
// ============================================================================

// Global variable for selected barcode image
let selectedBarcodeImage = null;

// Handle Barcode Image Selection
function handleBarcodeImageSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedBarcodeImage = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById('imagePreview').innerHTML =
                `<img src="${e.target.result}" style="max-width: 300px; max-height: 200px; border-radius: 8px;" alt="Barcode Preview">`;
        };
        reader.readAsDataURL(file);

        // Enable scan button
        document.getElementById('scanImageBtn').disabled = false;
    }
}

// Scan Barcode from Image
async function scanBarcodeImage() {
    if (!selectedBarcodeImage) {
        showResponse('scanResponse', '❌ Please select an image first!', 'error');
        return;
    }

    try {
        showResponse('scanResponse', '🔍 Detecting barcode in image...', 'info');

        const formData = new FormData();
        formData.append('image', selectedBarcodeImage);

        const response = await fetch(`${API_URL}/barcode/image`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            scannedProductData = result.product;
            showResponse('scanResponse', `✅ Barcode detected: ${result.barcode}\nProduct found!`, 'success');

            // Display product information
            displayProductInfo(scannedProductData);

            // Show product section
            document.getElementById('productSection').classList.remove('hidden');

            // Enable analyze button
            document.getElementById('analyzeBtn').disabled = false;
        } else {
            showResponse('scanResponse', `❌ ${result.error}\n${result.suggestion || ''}`, 'error');
            document.getElementById('productSection').classList.add('hidden');
        }
    } catch (error) {
        showResponse('scanResponse', `❌ Network Error: ${error.message}\n\nMake sure the API server is running and barcode detection libraries are installed!`, 'error');
    }
}

// Scan Barcode Number
async function scanBarcode() {
    const barcode = document.getElementById('barcodeInput').value.trim();

    if (!barcode) {
        showResponse('scanResponse', '❌ Please enter a barcode number', 'error');
        return;
    }

    try {
        showResponse('scanResponse', '🔍 Scanning barcode...', 'info');

        const response = await fetch(`${API_URL}/barcode/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ barcode: barcode })
        });

        const result = await response.json();

        if (response.ok) {
            scannedProductData = result.product;
            showResponse('scanResponse', '✅ Product found!', 'success');

            // Display product information
            displayProductInfo(scannedProductData);

            // Show product section
            document.getElementById('productSection').classList.remove('hidden');

            // Enable analyze button
            document.getElementById('analyzeBtn').disabled = false;
        } else {
            showResponse('scanResponse', `❌ ${result.error}`, 'error');
            document.getElementById('productSection').classList.add('hidden');
        }
    } catch (error) {
        showResponse('scanResponse', `❌ Network Error: ${error.message}\n\nMake sure the API server is running and API keys are configured!`, 'error');
    }
}

// Display Product Information
function displayProductInfo(product) {
    document.getElementById('productName').textContent = product.name || '-';
    document.getElementById('productBrand').textContent = product.brand || '-';
    document.getElementById('productCategory').textContent = product.category || '-';
    document.getElementById('productPrice').textContent = product.price ? product.price.toFixed(2) : '-';

    // Display nutrition facts
    const nutritionDiv = document.getElementById('nutritionInfo');
    if (product.nutrition && Object.keys(product.nutrition).length > 0) {
        let nutritionHTML = '<ul style="list-style: none; padding: 0;">';
        for (const [key, value] of Object.entries(product.nutrition)) {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            nutritionHTML += `<li style="padding: 5px 0; border-bottom: 1px solid #eee;">
                <strong>${label}:</strong> ${value}
            </li>`;
        }
        nutritionHTML += '</ul>';
        nutritionDiv.innerHTML = nutritionHTML;
    } else {
        nutritionDiv.innerHTML = '<p style="color: #999;">No nutrition information available</p>';
    }
}

// Analyze Product with AI Agents
async function analyzeProduct() {
    if (!scannedProductData) {
        showResponse('analysisResponse', '❌ Please scan a barcode first!', 'error');
        return;
    }

    try {
        showResponse('analysisResponse', '🤖 AI Agents are evaluating the product...\n\n' +
            'Health Agent: Analyzing nutritional alignment...\n' +
            'Fitness Agent: Checking fitness goal compatibility...\n' +
            'Price Agent: Evaluating value for money...', 'info');

        const response = await fetch(`${API_URL}/agent/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product: scannedProductData })
        });

        const result = await response.json();

        if (response.ok) {
            showResponse('analysisResponse', '✅ AI evaluation complete!', 'success');

            // Display evaluation results
            displayEvaluation(result.evaluation);

            // Show evaluation section
            document.getElementById('evaluationSection').classList.remove('hidden');
        } else {
            showResponse('analysisResponse', `❌ ${result.error}`, 'error');
        }
    } catch (error) {
        showResponse('analysisResponse', `❌ Network Error: ${error.message}`, 'error');
    }
}

// Display AI Evaluation Results
function displayEvaluation(evaluation) {
    // Overall score
    const overall = evaluation.overall;
    document.getElementById('overallEmoji').textContent = overall.recommendation_emoji;
    document.getElementById('overallRating').textContent = `Score: ${overall.score}/100`;
    document.getElementById('overallRecommendation').textContent = overall.recommendation;

    // Health analysis
    const health = evaluation.health_analysis;
    document.getElementById('healthScore').textContent = health.score;
    document.getElementById('healthSummary').innerHTML = health.summary;

    if (health.pros && health.pros.length > 0) {
        document.getElementById('healthPros').innerHTML =
            '<p><strong>✅ Pros:</strong></p><ul>' +
            health.pros.map(pro => `<li>${pro}</li>`).join('') +
            '</ul>';
    }

    if (health.cons && health.cons.length > 0) {
        document.getElementById('healthCons').innerHTML =
            '<p><strong>⚠️ Cons:</strong></p><ul>' +
            health.cons.map(con => `<li>${con}</li>`).join('') +
            '</ul>';
    }

    // Fitness analysis
    const fitness = evaluation.fitness_analysis;
    document.getElementById('fitnessScore').textContent = fitness.score;
    document.getElementById('fitnessSummary').innerHTML = fitness.summary;

    if (fitness.best_for) {
        document.getElementById('fitnessBestFor').innerHTML =
            `<p><strong>Best for:</strong> ${fitness.best_for}</p>`;
    }

    if (fitness.recommendation) {
        document.getElementById('fitnessRec').innerHTML =
            `<p><strong>Recommendation:</strong> ${fitness.recommendation}</p>`;
    }

    // Price analysis
    const price = evaluation.price_analysis;
    document.getElementById('priceRating').textContent = price.rating || '-';
    document.getElementById('priceSummary').innerHTML = price.summary || '-';
}

