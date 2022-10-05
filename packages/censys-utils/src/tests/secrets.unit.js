/* eslint-env jest */
import { assert } from 'chai';

import * as url from '@splunk/splunk-utils/url';

import secrets from '../secrets';
import { ERROR, PASSWORD, PASSWORDS, UPDATE_ERROR, makeUrl } from './utils';

const ENTRY_TITLE = `${secrets.DEFAULT_REALM}:${secrets.DEFAULT_SECRET_NAME}:`;
const TEST_SECRETS = {
    censys_asm_api_key: 'test',
    censys_search_app_id: 'test',
    censys_search_app_secret: 'test',
};

jest.spyOn(url, 'createRESTURL').mockImplementation(makeUrl);

const assertEntryIsValid = (
    entry,
    expectedTitle = ENTRY_TITLE,
    expectedUsername = secrets.DEFAULT_SECRET_NAME,
    expectPassword = true
) => {
    assert.isObject(entry);
    assert.equal(entry.title, expectedTitle);
    assert.equal(entry.username, expectedUsername);
    if (expectPassword) {
        assert.isObject(entry.clearPassword);
        assert.isString(entry.clearPassword.censys_asm_api_key);
        assert.isString(entry.clearPassword.censys_search_app_id);
        assert.isString(entry.clearPassword.censys_search_app_secret);
    } else {
        assert.isUndefined(entry.clearPassword);
    }
};

describe('CensysSetupUtils', () => {
    beforeEach(() => {
        fetch.resetMocks();
    });
    it('gets secret entries', async () => {
        fetch.mockResponseOnce(PASSWORDS, {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
            url: makeUrl('storage/passwords'),
        });
        const secretEntries = await secrets.getSecretEntries();
        assert.equal(secretEntries.length, 1);
        const secretEntry = secretEntries[0];
        assertEntryIsValid(secretEntry);
    });
    it('error getting secret entries', async () => {
        fetch.mockResponseOnce(ERROR, {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
            url: makeUrl('storage/passwords'),
        });
        await expect(secrets.getSecretEntries()).rejects.toThrowErrorMatchingSnapshot();
    });
    it('gets secret entry', async () => {
        fetch.mockResponseOnce(PASSWORDS, {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
            url: makeUrl('storage/passwords'),
        });
        const secretEntry = await secrets.getSecretEntry(secrets.DEFAULT_SECRET_NAME);
        assertEntryIsValid(secretEntry);
    });
    it('error getting secret entry', async () => {
        fetch.mockResponseOnce(ERROR, {
            status: 500,
            headers: { 'Content-Type': 'application/json' },
            url: makeUrl('storage/passwords'),
        });
        await expect(
            secrets.getSecretEntry(secrets.DEFAULT_SECRET_NAME)
        ).rejects.toThrowErrorMatchingSnapshot();
    });
    it('creates secret entry', async () => {
        fetch.mockResponseOnce(PASSWORD, {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
            url: makeUrl(`storage/passwords/${ENTRY_TITLE}`),
        });
        const secretEntry = await secrets.createSecretEntry(
            secrets.DEFAULT_SECRET_NAME,
            TEST_SECRETS
        );
        assertEntryIsValid(secretEntry, ENTRY_TITLE, secrets.DEFAULT_SECRET_NAME, false);
    });
    it('error creating secret entry', async () => {
        fetch.mockResponseOnce(ERROR, {
            status: 404,
            headers: { 'Content-Type': 'application/json' },
            url: makeUrl(`storage/passwords/${ENTRY_TITLE}`),
        });
        await expect(
            secrets.createSecretEntry(secrets.DEFAULT_SECRET_NAME, TEST_SECRETS)
        ).rejects.toThrowErrorMatchingSnapshot();
    });
    it('updates secret entry', async () => {
        fetch.mockResponseOnce(PASSWORD, {
            status: 200,
            headers: { 'Content-Type': 'application/json' },
            url: makeUrl(`storage/passwords/${ENTRY_TITLE}`),
        });
        const secretEntry = await secrets.updateSecretEntry(
            secrets.DEFAULT_SECRET_NAME,
            TEST_SECRETS
        );
        assertEntryIsValid(secretEntry, ENTRY_TITLE, secrets.DEFAULT_SECRET_NAME, false);
    });
    it('error updating secret entry', async () => {
        fetch.mockResponseOnce(UPDATE_ERROR, {
            status: 404,
            headers: { 'Content-Type': 'application/json' },
            url: makeUrl(`storage/passwords/${ENTRY_TITLE}`),
        });
        await expect(
            secrets.updateSecretEntry(secrets.DEFAULT_SECRET_NAME, TEST_SECRETS)
        ).rejects.toThrowErrorMatchingSnapshot();
    });
});
