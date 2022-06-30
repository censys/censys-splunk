import fetch from 'cross-fetch';
import 'url-search-params-polyfill';

import * as config from '@splunk/splunk-utils/config';
import { defaultFetchInit } from '@splunk/splunk-utils/fetch';
import { createRESTURL } from '@splunk/splunk-utils/url';

const DEFAULT_APP = 'censys';
const DEFAULT_SECRET_NAME = 'censys_app_secrets';
const DEFAULT_REALM = 'censys_setup';
const ASM_API_KEY_REGEX = /^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$/;
const SEARCH_API_ID_REGEX = ASM_API_KEY_REGEX;
const SEARCH_API_SECRET_REGEX = /^[a-z0-9]{32}$/i;

const app = config.app || DEFAULT_APP;

const findElementByName = (name, elements) => {
    for (let i = 0; i < elements.length; i += 1) {
        if (elements[i].getAttribute('name') === name) {
            return elements[i];
        }
    }
    return null;
};

const raiseOnError = (response) => {
    if (!response.ok) {
        throw Error(`${response.status} ${response.statusText}: ${response.url}`);
    }
    return response;
};

const parseEntry = (entryElement) => {
    const title = entryElement.getElementsByTagName('title')[0].textContent;
    const content = entryElement.getElementsByTagName('content')[0];
    const contentDict = content.getElementsByTagName('s:dict')[0];
    const contentDictKeys = contentDict.getElementsByTagName('s:key');
    let username = findElementByName('username', contentDictKeys);
    if (username) {
        username = username.textContent;
    }
    let clearPassword = findElementByName('clear_password', contentDictKeys);
    if (clearPassword) {
        clearPassword = clearPassword.textContent;
        try {
            clearPassword = JSON.parse(clearPassword);
        } catch (e) {
            // Ignore
        }
    }
    return {
        title,
        username,
        clearPassword,
    };
};

const parseXml = (xmlText) => {
    const parser = new DOMParser();
    return parser.parseFromString(xmlText, 'text/xml');
};

const getSecretEntries = (signal = null) => {
    const defaultErrorMsg = 'Unable to get secret entries';
    const url = createRESTURL('storage/passwords', {
        app,
        sharing: 'app',
    });

    // Get xml data from api and parse it to json
    return fetch(url, { ...defaultFetchInit, signal })
        .then(raiseOnError)
        .then((response) => response.text())
        .then((text) => {
            const xmlDoc = parseXml(text);
            const entries = xmlDoc.getElementsByTagName('entry');
            if (entries.length === 0) {
                throw new Error(defaultErrorMsg);
            }
            const secretEntries = [];
            for (let i = 0; i < entries.length; i += 1) {
                const entry = parseEntry(entries[i]);
                secretEntries.push(entry);
            }
            return secretEntries;
        });
    // .catch((error) => {
    //     // console.error(defaultErrorMsg, error);
    //     return [];
    // });
};

const getSecretEntry = (secretName, signal = null) => {
    const defaultErrorMsg = 'Unable to get secret entry';

    return getSecretEntries(signal).then((secretEntries) => {
        const secretEntry = secretEntries.find((entry) => entry.username === secretName);
        if (!secretEntry) {
            throw new Error(defaultErrorMsg);
        }
        return secretEntry;
    });
    // .catch((error) => {
    //     // console.error(defaultErrorMsg, error);
    //     return null;
    // });
};

const createSecretEntry = (secretName, secrets, signal = null) => {
    const defaultErrorMsg = 'Unable to set secret entries';
    const url = createRESTURL('storage/passwords', {
        app,
        sharing: 'app',
    });

    // Create form data to send
    const data = new URLSearchParams();
    data.append('name', secretName);
    data.append('password', JSON.stringify(secrets));
    data.append('realm', DEFAULT_REALM);

    // Make a POST request to set the secret entries
    return fetch(url, {
        ...defaultFetchInit,
        signal,
        method: 'POST',
        body: data,
        headers: {
            ...defaultFetchInit.headers,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(raiseOnError)
        .then((response) => response.text())
        .then((text) => {
            const xmlDoc = parseXml(text);
            const entryElements = xmlDoc.getElementsByTagName('entry');
            if (entryElements.length === 0) {
                throw new Error(defaultErrorMsg);
            }
            const entryElement = entryElements[0];
            return parseEntry(entryElement);
        });
    // .catch((error) => {
    //     // console.error(defaultErrorMsg, error);
    //     return null;
    // });
};

const updateSecretEntry = (secretName, secrets, signal = null) => {
    const defaultErrorMsg = 'Unable to update secret entries';
    const url = createRESTURL(`storage/passwords/${DEFAULT_REALM}:${secretName}:`, {
        app,
        sharing: 'app',
    });

    // Create form data to send
    const data = new URLSearchParams();
    data.append('password', JSON.stringify(secrets));

    // Make a POST request to update the secret entries
    return fetch(url, {
        ...defaultFetchInit,
        signal,
        method: 'POST',
        body: data,
        headers: {
            ...defaultFetchInit.headers,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(raiseOnError)
        .then((response) => response.text())
        .then((text) => {
            const xmlDoc = parseXml(text);
            const entryElements = xmlDoc.getElementsByTagName('entry');
            if (entryElements.length === 0) {
                throw new Error(defaultErrorMsg);
            }
            const entryElement = entryElements[0];
            return parseEntry(entryElement);
        });
    // .catch((error) => {
    //     // console.error(defaultErrorMsg, error);
    //     return null;
    // });
};

const setIsConfigured = (isConfigured = 1, signal = null) => {
    // const defaultErrorMsg = 'Unable to set is_configured';
    const url = createRESTURL('configs/conf-app/install', {
        app,
        sharing: 'app',
    });

    // Create form data to send
    const data = new URLSearchParams();
    data.append('is_configured', isConfigured);

    // Make a POST request to set the is_configured
    return fetch(url, {
        ...defaultFetchInit,
        signal,
        method: 'POST',
        body: data,
        headers: {
            ...defaultFetchInit.headers,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
        .then(raiseOnError)
        .then((response) => response.text());
    // .catch((error) => {
    //     // console.error(defaultErrorMsg, error);
    //     return null;
    // });
};

const reloadApp = () => {
    // const defaultErrorMsg = 'Unable to reload app';
    const url = createRESTURL(`apps/local/${app}/_reload`, {
        app,
        sharing: 'app',
    });

    // Make a POST request to reload the app
    return fetch(url, {
        ...defaultFetchInit,
        method: 'POST',
    }).then(raiseOnError);
    // .catch((error) => {
    //     // console.error(defaultErrorMsg, error);
    //     return null;
    // });
};

export {
    findElementByName,
    getSecretEntries,
    getSecretEntry,
    createSecretEntry,
    updateSecretEntry,
    setIsConfigured,
    reloadApp,
    DEFAULT_APP,
    DEFAULT_SECRET_NAME,
    DEFAULT_REALM,
    ASM_API_KEY_REGEX,
    SEARCH_API_ID_REGEX,
    SEARCH_API_SECRET_REGEX,
};
