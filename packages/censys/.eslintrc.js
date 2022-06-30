module.exports = {
    extends: ['@splunk/eslint-config/browser-prettier', 'plugin:compat/recommended'],
    env: {
        browser: true,
        node: true,
    },
    rules: {
        'no-param-reassign': 0,
    },
};
