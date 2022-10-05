const path = require('path');
const webpackMerge = require('webpack-merge');
const baseComponentConfig = require('@splunk/webpack-configs/component.config').default;

module.exports = webpackMerge(baseComponentConfig, {
    entry: {
        CensysUtils: path.join(__dirname, 'src/index.js'),
    },
    output: {
        path: path.join(__dirname),
    },
});
