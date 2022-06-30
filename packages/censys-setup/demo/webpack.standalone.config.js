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
                res.sendFile(path.join(CENSYS_APP_STATIC_PATH, fileName), {
                    'Content-Type': 'application/font-woff',
                });
            });
            app.use('/static', (req, res) => {
                const fileName = req.url.split('/').pop();
                res.sendFile(path.join(CENSYS_APP_STATIC_PATH, fileName), {
                    'Content-Type': 'text/css',
                });
            });
            app.use('/servicesNS/nobody/censys/storage/passwords', (req, res) => {
                if (req.method === 'GET') {
                    res.sendFile(path.join(STANDALONE_PATH, 'passwords.xml'), {
                        'Content-Type': 'application/xml',
                    });
                } else if (req.method === 'POST') {
                    res.setHeader('Content-Type', 'application/xml');
                    res.sendFile(path.join(STANDALONE_PATH, 'password.xml'), {
                        'Content-Type': 'application/xml',
                    });
                }
            });
            app.use('/servicesNS/nobody/censys/configs/conf-app/install', (req, res) => {
                if (req.method === 'POST') {
                    res.setHeader('Content-Type', 'application/xml');
                    res.sendFile(path.join(STANDALONE_PATH, 'install.xml'), {
                        'Content-Type': 'application/xml',
                    });
                }
            });
            app.use('/servicesNS/nobody/censys/apps/local/censys/_reload', (req, res) => {
                if (req.method === 'POST') {
                    res.setHeader('Content-Type', 'application/xml');
                    res.sendFile(path.join(STANDALONE_PATH, 'reload.xml'), {
                        'Content-Type': 'application/xml',
                    });
                }
            });
        },
    },
});
