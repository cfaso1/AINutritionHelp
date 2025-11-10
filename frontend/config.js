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
        // Production API URL for Render backend
        API_URL: 'https://balancebotapi.onrender.com/api',
        DEBUG: false
    }
};

// Export the active configuration
const ENV = getEnvironment();
const Config = config[ENV];

// Add console logging helper
Config.log = function(...args) {
    if (this.DEBUG) {
        console.log('[BalanceBot]', ...args);
    }
};

Config.error = function(...args) {
    console.error('[BalanceBot]', ...args);
};

// Export to global scope
window.BalanceBotConfig = Config;
window.BalanceBotEnv = ENV;

console.log(`🍎 BalanceBot initialized in ${ENV} mode`);
console.log(`API URL: ${Config.API_URL}`);
