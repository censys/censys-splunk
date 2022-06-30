module.exports = {
    extends: ['@splunk/eslint-config/browser-prettier', 'plugin:compat/recommended'],
    plugins: ['jest'],
    env: {
        browser: true,
        'jest/globals': true,
        node: true,
    },
};
