/**
 * Frontend Configuration
 * This file is loaded before app.js and provides environment-based configuration
 */

// Detect environment based on hostname
const getEnvironment = () => {
    const hostname = window.location.hostname;

    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0') {
        return 'development';
    } else {
        return 'production';
    }
};

// Environment-specific configuration
const config = {
    development: {
        API_URL: 'http://localhost:5000/api',
        DEBUG: true
    },
    production: {
        // IMPORTANT: Update this with your Render backend URL after deployment
        // Example: 'https://your-app-name.onrender.com/api'
        API_URL: 'https://balancebotapi.onrender.com/',
        DEBUG: false
    }
};

// Export the active configuration
const ENV = getEnvironment();
const Config = config[ENV];

// Add console logging helper
Config.log = function(...args) {
    if (this.DEBUG) {
        console.log('[NutriScan]', ...args);
    }
};

Config.error = function(...args) {
    console.error('[NutriScan]', ...args);
};

// Export to global scope
window.NutriScanConfig = Config;
window.NutriScanEnv = ENV;

console.log(`🍎 NutriScan initialized in ${ENV} mode`);
console.log(`API URL: ${Config.API_URL}`);
