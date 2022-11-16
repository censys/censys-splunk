import {
    config,
    createRESTURL,
    defaultFetchInit,
    fetch,
    getEntries,
    makeJsonUrl,
    raiseOnError,
} from './api';

export const ASM_RISKS_INPUT_TYPE = 'censys_asm_risks';
export const ASM_LOGBOOK_INPUT_TYPE = 'censys_asm_logbook';
export const INPUT_TYPES = [ASM_RISKS_INPUT_TYPE, ASM_LOGBOOK_INPUT_TYPE];

const defaultApp = config.app;

export const inputTypeNames = {
    [ASM_RISKS_INPUT_TYPE]: 'Censys ASM Risks',
    [ASM_LOGBOOK_INPUT_TYPE]: 'Censys ASM Logbook',
};

export const mapEntriesToInputs = (entries, inputType) => {
    return entries.map((entry) => {
        const { name, content } = entry;
        if (content) {
            const { interval, index, disabled } = content;
            return {
                name,
                type: inputType,
                interval,
                index,
                authentication: 'Global',
                disabled,
                selected: false,
            };
        }
        return {
            name,
            type: inputType,
        };
    });
};

export const getInputs = (inputType, app = defaultApp, signal = null) => {
    if (!INPUT_TYPES.includes(inputType)) {
        throw new Error(`Invalid input type: ${inputType}`);
    }

    const url = createRESTURL(`Splunk_TA_censys_${inputType}`, {
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
        .then(getEntries)
        .then((entries) => mapEntriesToInputs(entries, inputType));
};

export const createInput = (
    inputName,
    inputType,
    index,
    interval,
    app = defaultApp,
    signal = null
) => {
    if (!inputName) {
        throw Error('No input name provided');
    }
    if (!INPUT_TYPES.includes(inputType)) {
        throw new Error(`Invalid input type: ${inputType}`);
    }

    const url = createRESTURL(`Splunk_TA_censys_${inputType}`, {
        app,
        owner: 'nobody',
    });

    // Create form data to send
    const data = new URLSearchParams();
    data.append('name', inputName);
    data.append('index', index);
    data.append('interval', interval);

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
        .then((entries) => mapEntriesToInputs(entries, inputType));
};

export const deleteInput = (inputName, inputType, app = defaultApp, signal = null) => {
    if (!inputName) {
        throw Error('No input name provided');
    }
    if (!INPUT_TYPES.includes(inputType)) {
        throw new Error(`Invalid input type: ${inputType}`);
    }

    const url = createRESTURL(`Splunk_TA_censys_${inputType}/${inputName}`, {
        app,
        owner: 'nobody',
    });

    // Make a DELETE request to remove the input
    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'DELETE',
    })
        .then(raiseOnError)
        .then((response) => response.json());
};

export const updateInput = (
    inputName,
    inputType,
    index = null,
    interval = null,
    disabled = null,
    app = defaultApp,
    signal = null
) => {
    if (!inputName) {
        throw Error('No input name provided');
    }
    if (!INPUT_TYPES.includes(inputType)) {
        throw new Error(`Invalid input type: ${inputType}`);
    }

    const url = createRESTURL(`Splunk_TA_censys_${inputType}/${inputName}`, {
        app,
        owner: 'nobody',
    });

    // Create form data to send
    const data = new URLSearchParams();
    if (index !== null) {
        data.append('index', index);
    }
    if (interval !== null) {
        data.append('interval', interval);
    }
    if (disabled !== null) {
        data.append('disabled', disabled);
    }

    // Make a POST request to update the input
    return fetch(makeJsonUrl(url), {
        ...defaultFetchInit,
        signal,
        method: 'POST',
        body: data,
    })
        .then(raiseOnError)
        .then((response) => response.json());
};

export const setDisabledStatus = (
    inputName,
    inputType,
    disabled,
    app = defaultApp,
    signal = null
) => {
    return updateInput(inputName, inputType, null, null, disabled, app, signal);
};

export const mapEntriesToIndexes = (entries) => {
    return entries.map((entry) => {
        return entry.name;
    });
};

export const getIndexes = (count = -1, app = defaultApp, signal = null) => {
    const url = createRESTURL('data/indexes', {
        app,
        owner: 'nobody',
        sharing: 'app',
    });

    const params = new URLSearchParams();
    params.append('count', count);
    const paramsString = params.toString();

    return fetch(`${makeJsonUrl(url)  }&${paramsString}`, {
        ...defaultFetchInit,
        signal,
        method: 'GET',
    })
        .then(raiseOnError)
        .then((response) => response.json())
        .then(getEntries)
        .then(mapEntriesToIndexes);
};
