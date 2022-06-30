module.exports = {
    testMatch: ['**/*.unit.[jt]s?(x)'],
    automock: false,
    resetMocks: false,
    setupFilesAfterEnv: ['./setupJest.js'],
};
