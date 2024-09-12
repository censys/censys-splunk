import fetch from 'cross-fetch';
import 'url-search-params-polyfill';

import * as config from '@splunk/splunk-utils/config';
import { defaultFetchInit } from '@splunk/splunk-utils/fetch';
import { createRESTURL } from '@splunk/splunk-utils/url';

export const defaultApp = config.app;
export const appBaseUrl = `/app/${defaultApp}`;

export const raiseOnError = (response) => {
    if (!response.ok) {
        throw Error(`${response.status} ${response.statusText}: ${response.url}`);
    }
    return response;
};

export const makeJsonUrl = (url) => {
    const params = new URLSearchParams();
    params.append('output_mode', 'json');
    const paramsString = params.toString();
    if (url.indexOf('?') === -1) {
        return `${url}?${paramsString}`;
    }
    return `${url}&${paramsString}`;
};

export const getEntries = (res, raiseOnEmpty = false) => {
    const entries = res.entry || [];
    if (raiseOnEmpty && entries.length === 0) {
        throw Error(`No entries found in response: ${res}`);
    }
    return entries;
};

export const setIsConfigured = (isConfigured = 1, app = defaultApp, signal = null) => {
    const url = createRESTURL('configs/conf-app/install', {
        app,
        sharing: 'app',
    });

    // Create form data to send
    const data = new URLSearchParams();
    data.append('is_configured', isConfigured);

    // Make a POST request to set the is_configured
    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'POST',
        body: data,
    })
        .then(raiseOnError)
        .then((response) => response.json());
};

export const reloadApp = (app = defaultApp, signal = null) => {
    const url = createRESTURL(`apps/local/${app}/_reload`, {
        app,
        sharing: 'app',
    });

    // Make a POST request to reload the app
    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'POST',
    })
        .then(raiseOnError)
        .then((response) => response.json());
};

export { fetch, createRESTURL, defaultFetchInit, config };
