const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpackMerge = require('webpack-merge');
const baseConfig = require('@splunk/webpack-configs/base.config').default;

const CENSYS_APP_STATIC_PATH = path.join(
    __dirname,
    '..',
    '..',
    'censys',
    'src',
    'main',
    'resources',
    'splunk',
    'appserver',
    'static'
);
const STANDALONE_PATH = path.join(__dirname, 'standalone');
const RISK_INPUTS_PATH = path.join(STANDALONE_PATH, 'risk_inputs.json');
const LOGBOOK_INPUTS_PATH = path.join(STANDALONE_PATH, 'logbook_inputs.json');
const INDEXES_PATH = path.join(STANDALONE_PATH, 'indexes.json');

const getStaticPath = (file) => path.join(CENSYS_APP_STATIC_PATH, file);

module.exports = webpackMerge(baseConfig, {
    entry: path.join(__dirname, 'demo'),
    plugins: [
        new HtmlWebpackPlugin({
            hash: true,
            template: path.join(__dirname, 'standalone/index.html'),
        }),
    ],
    devtool: 'eval-source-map',
    devServer: {
        before: (app) => {
            app.use('/static/fonts', (req, res) => {
                const fileName = req.url.split('/').pop();
                res.sendFile(getStaticPath(fileName), {
                    'Content-Type': 'application/font-woff',
                });
            });
            app.use('/static', (req, res) => {
                const fileName = req.url.split('/').pop();
                const options = {};
                if (fileName.endsWith('.css')) {
                    options['Content-Type'] = 'text/css';
                }
                res.sendFile(getStaticPath(fileName), options);
            });
            app.use('/servicesNS/nobody/-/Splunk_TA_censys_censys_asm_risks', (req, res) => {
                res.sendFile(RISK_INPUTS_PATH, {
                    'Content-Type': 'application/json',
                });
            });
            app.use('/servicesNS/nobody/-/Splunk_TA_censys_censys_asm_logbook', (req, res) => {
                res.sendFile(LOGBOOK_INPUTS_PATH, {
                    'Content-Type': 'application/json',
                });
            });
            app.use('/servicesNS/nobody/-/data/indexes', (req, res) => {
                res.sendFile(INDEXES_PATH, {
                    'Content-Type': 'application/json',
                });
            });
        },
    },
});
