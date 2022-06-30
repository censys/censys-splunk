import fs from 'fs';
import path from 'path';

const STANDALONE_PATH = path.resolve(__dirname, '../../demo/standalone');
const PASSWORD_PATH = path.join(STANDALONE_PATH, 'password.xml');
const PASSWORDS_PATH = path.join(STANDALONE_PATH, 'passwords.xml');
const PASSWORD_XML = fs.readFileSync(PASSWORD_PATH, 'utf8');
const PASSWORDS_XML = fs.readFileSync(PASSWORDS_PATH, 'utf8');
const ERROR_XML = `<?xml version="1.0" encoding="UTF-8"?>
<response>
  <messages>
    <msg type="ERROR">Unauthorized</msg>
  </messages>
</response>`;

const makeUrl = (endpoint) => `https://splunk.dev/service/${endpoint}`;

export { STANDALONE_PATH, PASSWORD_XML, PASSWORDS_XML, ERROR_XML, makeUrl };
