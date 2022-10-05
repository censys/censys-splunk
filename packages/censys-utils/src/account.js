import {
    config,
    createRESTURL,
    defaultFetchInit,
    fetch,
    getEntries,
    makeJsonUrl,
    raiseOnError,
} from './api';

const defaultApp = config.app;

export const getAccounts = (app = defaultApp, signal = null) => {
    const url = createRESTURL('Splunk_TA_censys_account', {
        app,
        owner: 'nobody',
        sharing: 'app',
    });

    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        method: 'GET',
        signal,
    })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries);
};

export const getAccount = (name, app = defaultApp, signal = null) => {
    const url = createRESTURL(`Splunk_TA_censys_account/${name}`, {
        app,
        owner: 'nobody',
        sharing: 'app',
    });

    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        method: 'GET',
        signal,
    })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries);
};

export const createAccount = (name, username, password, app = defaultApp, signal = null) => {
    const url = createRESTURL('Splunk_TA_censys_account', {
        app,
        owner: 'nobody',
        sharing: 'app',
    });

    const data = new URLSearchParams();
    data.append('name', name);
    data.append('username', username);
    data.append('password', password);

    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'POST',
        body: data,
    })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries);
};

export const updateAccount = (name, username, password, app = defaultApp, signal = null) => {
    const url = createRESTURL(`Splunk_TA_censys_account/${name}`, {
        app,
        owner: 'nobody',
        sharing: 'app',
    });

    const data = new URLSearchParams();
    data.append('username', username);
    data.append('password', password);

    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'PATCH',
        body: data,
    })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries);
};

export const deleteAccount = (name, app = defaultApp, signal = null) => {
    const url = createRESTURL(`Splunk_TA_censys_account/${name}`, {
        app,
        owner: 'nobody',
        sharing: 'app',
    });

    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'DELETE',
    })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries);
};
