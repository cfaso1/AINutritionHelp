// Configuration
const API_URL = 'http://localhost:5000/api';
let currentUser = null;
let profileData = {};
let scannedProduct = null;
let chatHistory = [];

const Screens = {
    WELCOME: 'welcomeScreen',
    PROFILE_SETUP: 'profileSetup',
    DASHBOARD: 'dashboard',
    SETTINGS: 'settingsPage'
};

// Screen Management
function showScreen(screenName) {
    Object.values(Screens).forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('show', 'hidden');
    });

    const element = document.getElementById(screenName);
    if (element) element.classList.add('show');

    if (screenName === Screens.WELCOME) updateNav(false);
    else if (screenName === Screens.PROFILE_SETUP) { updateNav(false); resetProfileSetup(); }
    else if (screenName === Screens.DASHBOARD) { updateNav(true); updateUserDisplay(); }
    else if (screenName === Screens.SETTINGS) { updateNav(true); loadSettingsData(); }
}

function resetProfileSetup() {
    document.querySelectorAll('.question-card').forEach(q => q.classList.remove('active'));
    document.getElementById('q1').classList.add('active');
    document.querySelectorAll('.progress-dot').forEach((dot, i) => {
        dot.classList.toggle('active', i === 0);
    });
    profileData = {};
}

function showWelcomeScreen() { showScreen(Screens.WELCOME); }
function showProfileSetup() { showScreen(Screens.PROFILE_SETUP); }
function showDashboard() { showScreen(Screens.DASHBOARD); }
function showSettings() { showScreen(Screens.SETTINGS); }

// Navigation
function updateNav(loggedIn) {
    document.getElementById('navButtons').style.display = loggedIn ? 'none' : 'flex';
    document.getElementById('userBannerNav').classList.toggle('show', loggedIn);
}

function updateUserDisplay() {
    if (!currentUser) return;
    document.getElementById('userAvatar').textContent = currentUser.username.substring(0, 2).toUpperCase();
    document.getElementById('userName').textContent = currentUser.username;

    if (currentUser.profile && currentUser.profile.goal_type) {
        const goalText = currentUser.profile.goal_type.replace('_', ' ');
        document.getElementById('userGoal').textContent = 'Goal: ' + goalText.charAt(0).toUpperCase() + goalText.slice(1);
    } else {
        document.getElementById('userGoal').textContent = 'Complete your profile';
    }
}

// Modal Management
function showLogin() {
    closeModal();
    document.getElementById('loginModal').classList.add('show');
}

function showSignup() {
    closeModal();
    document.getElementById('signupModal').classList.add('show');
}

function closeModal() {
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('show'));
    document.querySelectorAll('.message').forEach(m => m.classList.remove('show'));
}

function showMessage(elementId, message, type = 'error') {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.className = `message show ${type}`;
    setTimeout(() => el.classList.remove('show'), 5000);
}

// Authentication
async function handleSignup(e) {
    e.preventDefault();
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const result = await response.json();

        if (response.ok) {
            currentUser = { user_id: result.user_id, username, email, profile: null };
            localStorage.setItem('nutriscan_user', JSON.stringify(currentUser));
            closeModal();
            showProfileSetup();
        } else {
            showMessage('signupMessage', result.error || 'Signup failed', 'error');
        }
    } catch (error) {
        showMessage('signupMessage', 'Network error. Please try again.', 'error');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const result = await response.json();

        if (response.ok) {
            currentUser = result.user;
            localStorage.setItem('nutriscan_user', JSON.stringify(currentUser));
            closeModal();

            await loadUserProfile();
            const complete = hasProfile(currentUser.profile);
            complete ? showDashboard() : showProfileSetup();
        } else {
            showMessage('loginMessage', result.error || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('loginMessage', 'Network error. Try: demo_user / demo123', 'error');
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('nutriscan_user');
    location.reload();
}

async function loadUserProfile() {
    try {
        const response = await fetch(`${API_URL}/profile`);
        if (response.ok) {
            const result = await response.json();
            currentUser.profile = result.profile;
            localStorage.setItem('nutriscan_user', JSON.stringify(currentUser));
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

// Profile Setup
function nextQuestion(num) {
    if (num === 2) {
        const height = document.getElementById('profileHeight').value.trim();
        const weight = document.getElementById('profileWeight').value.trim();
        const gender = document.getElementById('profileGender').value;
        const age = document.getElementById('profileAge').value;

        if (!gender) { alert("Please select your gender."); return; }
        if (!age) { alert("Please select your age range."); return; }

        const heightPattern = /^\d+'\d{1,2}$/;
        if (!heightPattern.test(height)) {
            alert("Height must be in format 5'8");
            return;
        }

        const [feet, inches] = height.split("'").map(Number);
        if (feet < 3 || feet > 8 || inches < 0 || inches > 11) {
            alert("Invalid height range");
            return;
        }

        const weightVal = parseFloat(weight);
        if (!weightVal || weightVal < 66 || weightVal > 660) {
            alert("Weight must be between 66 and 660 pounds");
            return;
        }

        profileData.height = height;
        profileData.weight = weightVal;
        profileData.gender = gender;
        profileData.age_category = age;
    }

    document.querySelectorAll('.question-card').forEach(q => q.classList.remove('active'));
    const target = document.getElementById(`q${num}`);
    if (target) target.classList.add('active');

    document.querySelectorAll('.progress-dot').forEach((dot, i) => {
        dot.classList.toggle('active', i < num);
    });
}

function setProfileData(key, value) {
    profileData[key] = value;
}

async function submitProfile() {
    try {
        const heightRaw = (profileData.height || '').toString().trim();
        const weightRaw = (profileData.weight || '').toString().trim();

        const heightPattern = /^\d+'\d{1,2}$/;
        if (!heightPattern.test(heightRaw)) {
            alert("Height must be in format 5'8");
            return;
        }

        const weightVal = parseFloat(weightRaw);
        if (Number.isNaN(weightVal) || weightVal <= 0) {
            alert('Please enter a valid weight in pounds');
            return;
        }

        const dietaryRestrictions = [];
        document.querySelectorAll('.dietary-restriction-checkbox:checked').forEach(checkbox => {
            if (checkbox.value !== 'none') dietaryRestrictions.push(checkbox.value);
        });

        const payload = {
            height: heightRaw,
            current_weight_lbs: weightVal,
            gender: profileData.gender,
            age_category: profileData.age_category,
            goal_type: profileData.goal,
            activity_level: profileData.activity,
            diet_type: profileData.diet,
            dietary_restrictions: dietaryRestrictions.join(', ')
        };

        const response = await fetch(`${API_URL}/profile/setup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            await loadUserProfile();
            showDashboard();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to save profile');
        }
    } catch (error) {
        alert('Failed to save profile. Please try again.');
    }
}

// Settings
function loadSettingsData() {
    if (!currentUser || !currentUser.profile) return;
    const p = currentUser.profile;

    if (p.height_feet !== null && p.height_inches !== null) {
        document.getElementById('editHeight').value = `${p.height_feet}'${p.height_inches}`;
    } else if (p.height_cm) {
        const totalInches = p.height_cm / 2.54;
        const feet = Math.floor(totalInches / 12);
        const inches = Math.round(totalInches - feet * 12);
        document.getElementById('editHeight').value = `${feet}'${inches}`;
    }

    if (p.weight_lbs) {
        document.getElementById('editWeight').value = Math.round(p.weight_lbs);
    } else if (p.current_weight_kg) {
        document.getElementById('editWeight').value = Math.round(p.current_weight_kg / 0.453592);
    }

    document.getElementById('editGoal').value = p.goal_type || 'general_health';
    document.getElementById('editActivity').value = p.activity_level || 'moderately_active';
    document.getElementById('editDiet').value = p.diet_type || 'standard';
    document.getElementById('editGender').value = p.gender || 'male';
    document.getElementById('editAge').value = p.age_category || '26-35';
    document.getElementById('editDietaryRestrictions').value = p.dietary_restrictions || '';
}

async function saveProfile() {
    const height = document.getElementById('editHeight').value.trim();
    const weight = document.getElementById('editWeight').value.trim();
    const gender = document.getElementById('editGender').value;
    const age = document.getElementById('editAge').value;
    const restrictions = document.getElementById('editDietaryRestrictions').value.trim();

    const heightPattern = /^\d+'\d{1,2}$/;
    if (!heightPattern.test(height)) {
        showMessage('settingsMessage', "Height must be in format 5'8", 'error');
        return;
    }

    const weightVal = parseFloat(weight);
    if (Number.isNaN(weightVal) || weightVal <= 0) {
        showMessage('settingsMessage', 'Please enter a valid weight', 'error');
        return;
    }

    const updatedProfile = {
        height: height,
        current_weight_lbs: Math.round(weightVal),
        gender: gender,
        age_category: age,
        goal_type: document.getElementById('editGoal').value,
        activity_level: document.getElementById('editActivity').value,
        diet_type: document.getElementById('editDiet').value,
        dietary_restrictions: restrictions
    };

    try {
        const response = await fetch(`${API_URL}/profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedProfile)
        });

        if (response.ok) {
            await loadUserProfile();
            showMessage('settingsMessage', 'Profile updated successfully!', 'success');
            setTimeout(() => showDashboard(), 2000);
        } else {
            const resJson = await response.json().catch(() => ({}));
            showMessage('settingsMessage', resJson.error || 'Failed to update profile', 'error');
        }
    } catch (error) {
        showMessage('settingsMessage', 'Network error', 'error');
    }
}

// Image Upload & Scanning
async function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    showLoading();
    hideResults();

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch(`${API_URL}/nutrition/ocr`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        hideLoading();

        if (result.success) {
            if (result.needs_clarification) {
                showClarificationForm(result.data, result.clarification_fields, result.message);
            } else {
                scannedProduct = { name: 'Scanned Product', nutrition: result.data, price: null };
                askForPrice(result.data);
            }
        } else if (result.needs_manual_entry) {
            showMessageBox(result.error || 'OCR failed. Please enter nutrition facts manually.', 'error');
            setTimeout(() => showManualInput(), 1500);
        } else {
            showMessageBox(result.error || 'Failed to process image', 'error');
        }
    } catch (error) {
        hideLoading();
        showMessageBox('Network error! Please try again.', 'error');
    }
}

function displayProduct(product) {
    document.getElementById('productName').textContent = product.name || 'Unknown';
    document.getElementById('productBrand').textContent = product.brand || 'Unknown';
    document.getElementById('productCategory').textContent = product.category || 'Uncategorized';
    document.getElementById('productPrice').textContent = product.price ? product.price.toFixed(2) : '0.00';

    const grid = document.getElementById('nutritionGrid');
    grid.innerHTML = '';

    if (product.nutrition) {
        const nutrients = [
            { key: 'calories', label: 'Calories', unit: '' },
            { key: 'protein', label: 'Protein', unit: 'g' },
            { key: 'carbohydrates', label: 'Carbs', unit: 'g' },
            { key: 'sugar', label: 'Sugar', unit: 'g' },
            { key: 'fat', label: 'Fat', unit: 'g' },
            { key: 'sodium', label: 'Sodium', unit: 'mg' }
        ];

        nutrients.forEach(n => {
            const value = product.nutrition[n.key] || 0;
            grid.innerHTML += `
                <div class="stat-box">
                    <span class="stat-value">${value}${n.unit}</span>
                    <span class="stat-label">${n.label}</span>
                </div>
            `;
        });
    }

    document.getElementById('resultsPanel').classList.add('show');
    document.getElementById('analyzeBtn').disabled = false;
}

async function analyzeProduct() {
    if (!scannedProduct) {
        showMessageBox('Please scan a product first', 'error');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_URL}/agent/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product: scannedProduct })
        });

        const result = await response.json();
        hideLoading();

        if (response.ok) {
            displayAIResults(result.evaluation);
        } else {
            showMessageBox(result.error || 'Analysis failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showMessageBox('Network error during analysis', 'error');
    }
}

function displayAIResults(evaluation) {
    document.getElementById('overallScore').textContent = evaluation.overall.score + '/100';
    document.getElementById('overallRecommendation').textContent =
        (evaluation.overall.recommendation_emoji || '') + ' ' + evaluation.overall.recommendation;

    document.getElementById('healthScore').textContent = evaluation.health_analysis.score;
    document.getElementById('healthSummary').textContent = evaluation.health_analysis.summary;

    if (evaluation.health_analysis.pros && evaluation.health_analysis.pros.length) {
        document.getElementById('healthPros').innerHTML =
            '<strong style="color: var(--primary-green);">Benefits:</strong><ul style="margin-left: 20px; margin-top: 10px;">' +
            evaluation.health_analysis.pros.map(p => `<li style="margin: 5px 0;">${p}</li>`).join('') +
            '</ul>';
    }

    if (evaluation.health_analysis.cons && evaluation.health_analysis.cons.length) {
        document.getElementById('healthCons').innerHTML =
            '<strong style="color: #d32f2f;">Considerations:</strong><ul style="margin-left: 20px; margin-top: 10px;">' +
            evaluation.health_analysis.cons.map(c => `<li style="margin: 5px 0;">${c}</li>`).join('') +
            '</ul>';
    }

    document.getElementById('fitnessScore').textContent = evaluation.fitness_analysis.score;
    document.getElementById('fitnessSummary').textContent = evaluation.fitness_analysis.summary;
    document.getElementById('fitnessBestFor').textContent = evaluation.fitness_analysis.best_for || '-';
    document.getElementById('fitnessRec').textContent = evaluation.fitness_analysis.recommendation || '-';

    document.getElementById('priceRating').textContent = evaluation.price_analysis.rating || '-';
    document.getElementById('priceSummary').textContent = evaluation.price_analysis.summary || '-';

    document.getElementById('aiResults').style.display = 'block';
    showMessageBox('Analysis complete!', 'success');

    sendEvaluationToChat(evaluation);
}

function showLoading() { document.getElementById('loading').classList.add('show'); }
function hideLoading() { document.getElementById('loading').classList.remove('show'); }
function hideResults() {
    document.getElementById('resultsPanel').classList.remove('show');
    document.getElementById('aiResults').style.display = 'none';
}
function showMessageBox(message, type) {
    const box = document.getElementById('messageBox');
    box.textContent = message;
    box.className = `message show ${type}`;
    setTimeout(() => box.classList.remove('show'), 5000);
}

// Manual Entry
function showManualInput() {
    const html = `
        <div class="manual-input-container">
            <div class="manual-input-header">
                <h3>Manual Nutrition Entry</h3>
                <p>Enter the nutrition facts from your product label</p>
            </div>
            <form id="manualNutritionForm" onsubmit="submitManualEntry(event)">
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Calories *</label>
                        <input type="number" step="1" name="calories" placeholder="250" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Protein (g) *</label>
                        <input type="number" step="0.1" name="protein" placeholder="8.5" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Total Carbs (g) *</label>
                        <input type="number" step="0.1" name="carbs_total" placeholder="45.0" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Total Sugar (g) *</label>
                        <input type="number" step="0.1" name="sugar_total" placeholder="12.0" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Total Fat (g) *</label>
                        <input type="number" step="0.1" name="fat_total" placeholder="10.0" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Saturated Fat (g)</label>
                        <input type="number" step="0.1" name="saturated_fat" placeholder="3.0">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Sodium (mg) *</label>
                        <input type="number" step="1" name="sodium" placeholder="200" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Cholesterol (mg) *</label>
                        <input type="number" step="1" name="cholesterol" placeholder="15" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Dietary Fiber (g)</label>
                        <input type="number" step="0.1" name="dietary_fiber" placeholder="3.5">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Trans Fat (g)</label>
                        <input type="number" step="0.1" name="trans_fat" placeholder="0.0">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Serving Size *</label>
                        <input type="text" name="serving_size" placeholder="100g or 1 cup" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Servings Per Container *</label>
                        <input type="number" step="0.1" name="servings_per_container" placeholder="2.5" required>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn primary">Submit Entry</button>
                    <button type="button" class="btn" onclick="hideManualInput()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    document.getElementById('results').innerHTML = html;
    document.getElementById('results').style.display = 'block';
}

function hideManualInput() {
    document.getElementById('results').style.display = 'none';
}

async function submitManualEntry(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const nutritionData = {};
    for (const [key, value] of formData.entries()) {
        if (value) nutritionData[key] = isNaN(value) ? value : parseFloat(value);
    }

    showLoading();

    try {
        const response = await fetch(`${API_URL}/nutrition/manual`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nutritionData)
        });

        const result = await response.json();
        hideLoading();

        if (result.success) {
            hideManualInput();
            scannedProduct = { name: 'Manual Entry', nutrition: result.data, price: null };
            askForPrice(result.data);
        } else {
            showMessageBox(result.error || 'Validation failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showMessageBox('Network error! Please try again.', 'error');
    }
}

function showClarificationForm(originalData, clarificationFields, message) {
    let fieldsHtml = '';
    for (const [fieldName, fieldInfo] of Object.entries(clarificationFields)) {
        const displayName = fieldInfo.display_name;
        const currentValue = fieldInfo.value || '';
        const status = fieldInfo.status;
        const statusBadge = status === 'missing' ?
            '<span style="color: red; font-size: 0.8em;">(Missing)</span>' :
            `<span style="color: orange; font-size: 0.8em;">(Low Confidence: ${(fieldInfo.confidence * 100).toFixed(0)}%)</span>`;

        fieldsHtml += `
            <div class="form-group">
                <label class="form-label">${displayName} ${statusBadge}</label>
                <input type="text" class="form-input" name="${fieldName}"
                       value="${currentValue}" placeholder="Enter value">
            </div>
        `;
    }

    const html = `
        <div class="manual-input-container" style="max-width: 600px;">
            <h3 style="color: var(--primary-green); margin-bottom: 15px; text-align: center;">Verify Nutrition Data</h3>
            <p style="color: var(--medium-text); margin-bottom: 25px; text-align: center;">${message}</p>
            <form id="clarificationForm" onsubmit="submitClarification(event)">
                <div class="form-grid">${fieldsHtml}</div>
                <div class="form-actions">
                    <button type="submit" class="btn primary">Confirm</button>
                    <button type="button" class="btn" onclick="showManualInput()">Manual Entry Instead</button>
                </div>
            </form>
        </div>
    `;

    window.ocrOriginalData = originalData;
    document.getElementById('results').innerHTML = html;
    document.getElementById('results').style.display = 'block';
}

async function submitClarification(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const corrections = {};
    for (const [key, value] of formData.entries()) {
        if (value) corrections[key] = value;
    }

    showLoading();

    try {
        const response = await fetch(`${API_URL}/nutrition/clarify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_data: window.ocrOriginalData,
                corrections: corrections
            })
        });

        const result = await response.json();
        hideLoading();

        if (result.success) {
            document.getElementById('results').style.display = 'none';
            scannedProduct = { name: 'Scanned Product', nutrition: result.data, price: null };
            askForPrice(result.data);
        } else {
            showMessageBox(result.error || 'Validation failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showMessageBox('Network error! Please try again.', 'error');
    }
}

function askForPrice(nutritionData) {
    const html = `
        <div class="manual-input-container" style="max-width: 500px; text-align: center;">
            <h3 style="color: var(--primary-green); margin-bottom: 15px;">Add Price (Optional)</h3>
            <p style="color: var(--medium-text); margin-bottom: 25px;">
                Enter the product price to get a value-for-money analysis
            </p>
            <form id="priceForm" onsubmit="submitPrice(event)">
                <div class="form-group">
                    <label class="form-label">Price ($)</label>
                    <input type="number" step="0.01" name="price" class="form-input"
                           placeholder="0.00" style="font-size: 1.2rem; text-align: center;">
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn primary">Continue</button>
                    <button type="button" class="btn" onclick="submitPrice(null)">Skip</button>
                </div>
            </form>
        </div>
    `;

    window.pendingNutritionData = nutritionData;
    document.getElementById('results').innerHTML = html;
    document.getElementById('results').style.display = 'block';
}

async function submitPrice(event) {
    let price = null;
    if (event && event.preventDefault) {
        event.preventDefault();
        const formData = new FormData(event.target);
        price = formData.get('price');
        price = price ? parseFloat(price) : null;
    }

    const productData = {
        name: scannedProduct.name,
        brand: 'N/A',
        category: 'Food',
        price: price,
        ...window.pendingNutritionData
    };

    await evaluateProduct(productData);
}

async function evaluateProduct(productData) {
    showLoading();

    try {
        const response = await fetch(`${API_URL}/agent/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product: scannedProduct })
        });

        const result = await response.json();
        hideLoading();

        if (result.success) {
            displayEvaluation(result.evaluation, productData);
            showMessageBox('Analysis complete!', 'success');
        } else {
            showMessageBox(result.error || 'Evaluation failed', 'error');
        }
    } catch (error) {
        hideLoading();
        showMessageBox('Network error! Please try again.', 'error');
    }
}

function displayEvaluation(evaluation, product) {
    const html = `
        <div class="manual-input-container">
            <h2 style="color: var(--primary-green); margin-bottom: 25px; text-align: center;">Nutrition Analysis</h2>
            <div style="background: var(--mint); padding: 20px; border-radius: 12px; margin-bottom: 25px;">
                <h3 style="color: var(--primary-green); margin-bottom: 10px;">${product.name || 'Product'}</h3>
                ${product.price ? `<p style="color: var(--medium-text);">Price: $${product.price.toFixed(2)}</p>` : ''}
            </div>
            <div style="white-space: pre-wrap; line-height: 1.8; color: var(--dark-text);">
                ${evaluation.summary || evaluation}
            </div>
            <button class="btn primary" onclick="resetScanner()" style="margin-top: 25px; width: 100%;">
                Scan Another Product
            </button>
        </div>
    `;

    document.getElementById('results').innerHTML = html;
    document.getElementById('results').style.display = 'block';
}

function resetScanner() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('results').innerHTML = '';
    document.getElementById('imageInput').value = '';
    scannedProduct = null;
    window.ocrOriginalData = null;
    window.pendingNutritionData = null;
}

// Chat Functions
function parseMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

function addChatMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chatMessages');
    const chatWelcome = document.getElementById('chatWelcome');
    if (chatWelcome) chatWelcome.style.display = 'none';

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'ai'}`;

    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar';
    avatar.textContent = isUser ? '👤' : '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    bubble.innerHTML = parseMarkdown(message);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);

    const typingIndicator = document.getElementById('typingIndicator');
    chatMessages.insertBefore(messageDiv, typingIndicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    chatHistory.push({ message, isUser, timestamp: new Date() });
}

function showTypingIndicator() {
    document.getElementById('typingIndicator').style.display = 'flex';
    document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
}

function hideTypingIndicator() {
    document.getElementById('typingIndicator').style.display = 'none';
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const message = chatInput.value.trim();

    if (!message) return;

    addChatMessage(message, true);
    chatInput.value = '';
    chatSendBtn.disabled = true;
    showTypingIndicator();

    try {
        const requestData = { message: message };
        if (scannedProduct) requestData.product = scannedProduct;

        const response = await fetch(`${API_URL}/agent/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const result = await response.json();
        hideTypingIndicator();

        if (response.ok) {
            addChatMessage(result.message, false);
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again!', false);
        }
    } catch (error) {
        hideTypingIndicator();
        addChatMessage('Sorry, I\'m having trouble connecting. Please check your internet connection!', false);
    } finally {
        chatSendBtn.disabled = false;
        chatInput.focus();
    }
}

function sendQuickMessage(message) {
    document.getElementById('chatInput').value = message;
    sendChatMessage();
}

function sendEvaluationToChat(evaluation) {
    const chatWelcome = document.getElementById('chatWelcome');
    if (chatWelcome) chatWelcome.style.display = 'none';

    if (evaluation && evaluation.companion_message) {
        addChatMessage(evaluation.companion_message, false);
    } else {
        const product = evaluation.product || {};
        const overall = evaluation.overall || {};
        let message = `I analyzed ${product.name || 'this product'}!\n\n`;
        message += `Overall Score: ${overall.score || 0}/100\n`;
        message += `Recommendation: ${overall.recommendation || 'See details for more info'}`;
        addChatMessage(message, false);
    }

    document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight;
}

// Initialization
function hasProfile(p) {
    if (!p) return false;
    const hasHeight = (typeof p.height === 'string' && p.height.length > 0) ||
        (Number.isFinite(p.height_cm) && p.height_cm > 0) ||
        (Number.isFinite(p.height_feet) && Number.isFinite(p.height_inches));
    const hasGoal = !!p.goal_type;
    return hasHeight && hasGoal;
}

function init() {
    const savedUser = localStorage.getItem('nutriscan_user');

    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            const complete = hasProfile(currentUser.profile);
            complete ? showDashboard() : showProfileSetup();
        } catch (error) {
            localStorage.removeItem('nutriscan_user');
            showWelcomeScreen();
        }
    } else {
        showWelcomeScreen();
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
