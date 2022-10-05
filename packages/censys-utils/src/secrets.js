import {
    config,
    createRESTURL,
    defaultFetchInit,
    fetch,
    getEntries,
    makeJsonUrl,
    raiseOnError,
} from './api';

const DEFAULT_SECRET_NAME = 'censys_secrets';
const DEFAULT_REALM = 'censys_setup';
const ASM_API_KEY_REGEX = /^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$/;
const SEARCH_API_ID_REGEX = ASM_API_KEY_REGEX;
const SEARCH_API_SECRET_REGEX = /^[a-z0-9]{32}$/i;

const mapEntryToSecretEntry = (entry) => {
    const { name, content } = entry;
    if (content) {
        const { username, realm } = content;
        let clearPassword = content.clear_password;
        try {
            clearPassword = JSON.parse(clearPassword);
        } catch (error) {
            // do nothing
        }
        return {
            title: name,
            username,
            clearPassword,
            realm,
        };
    }
    return null;
};

const mapEntriesToSecretEntries = (entries) => {
    return entries.map(mapEntryToSecretEntry).filter((entry) => entry !== null);
};

const getSecretEntries = (app = config.app, signal = null) => {
    const url = createRESTURL('storage/passwords', {
        app,
        sharing: 'app',
    });

    return fetch(makeJsonUrl(url), { ...defaultFetchInit, signal })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries)
        .then(mapEntriesToSecretEntries);
};

const getSecretEntry = (secretName, app = config.app, signal = null) => {
    const defaultErrorMsg = 'Unable to get secret entry';

    return getSecretEntries(signal, app).then((secretEntries) => {
        const secretEntry = secretEntries.find((entry) => entry.username === secretName);
        if (!secretEntry) {
            throw new Error(defaultErrorMsg);
        }
        return secretEntry;
    });
};

const createSecretEntry = (secretName, secrets, app = config.app, signal = null) => {
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
    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'POST',
        body: data,
    })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries)
        .then(mapEntriesToSecretEntries)
        .then((secretEntries) => {
            if (secretEntries.length === 0) {
                throw new Error('Unable to set secret entries');
            }
            return secretEntries[0];
        });
};

const updateSecretEntry = (secretName, secrets, app = config.app, signal = null) => {
    const url = createRESTURL(`storage/passwords/${DEFAULT_REALM}:${secretName}:`, {
        app,
        sharing: 'app',
    });

    // Create form data to send
    const data = new URLSearchParams();
    data.append('password', JSON.stringify(secrets));

    // Make a POST request to update the secret entries
    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'POST',
        body: data,
    })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries)
        .then(mapEntriesToSecretEntries)
        .then((secretEntries) => {
            if (secretEntries.length === 0) {
                throw new Error('Unable to update secret entries');
            }
            return secretEntries[0];
        });
};

export default {
    DEFAULT_SECRET_NAME,
    DEFAULT_REALM,
    ASM_API_KEY_REGEX,
    SEARCH_API_ID_REGEX,
    SEARCH_API_SECRET_REGEX,
    getSecretEntries,
    getSecretEntry,
    createSecretEntry,
    updateSecretEntry,
};
