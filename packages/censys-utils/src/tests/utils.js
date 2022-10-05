import fs from 'fs';
import path from 'path';

const CENSYS_SETUP_PATH = path.resolve(__dirname, '../../../censys-setup');
const STANDALONE_PATH = path.resolve(CENSYS_SETUP_PATH, 'demo/standalone');
const PASSWORD_PATH = path.join(STANDALONE_PATH, 'password.json');
const PASSWORDS_PATH = path.join(STANDALONE_PATH, 'passwords.json');
const PASSWORD = fs.readFileSync(PASSWORD_PATH, 'utf8');
const PASSWORDS = fs.readFileSync(PASSWORDS_PATH, 'utf8');
const ERROR = {
    messages: [
        {
            text: 'See Other',
            type: 'ERROR',
        },
    ],
};
const UPDATE_ERROR = {
    messages: [
        {
            type: 'ERROR',
            text: 'A password already exists for id="credential:censys_setup:censys_app_secrets:"',
        },
    ],
};

const makeUrl = (endpoint) => `https://splunk.dev/service/${endpoint}`;

export { STANDALONE_PATH, PASSWORD, PASSWORDS, ERROR, UPDATE_ERROR, makeUrl };
