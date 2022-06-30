/* eslint-env jest */
import { assert } from 'chai';

import * as url from '@splunk/splunk-utils/url';

import * as setupUtils from '../CensysSetupUtils';
import { ERROR_XML, PASSWORDS_XML, PASSWORD_XML, makeUrl } from './utils';

const ENTRY_TITLE = `${setupUtils.DEFAULT_REALM}:${setupUtils.DEFAULT_SECRET_NAME}:`;
const TEST_SECRETS = {
    censys_asm_api_key: 'test',
    censys_search_app_id: 'test',
    censys_search_app_secret: 'test',
};

jest.spyOn(url, 'createRESTURL').mockImplementation(makeUrl);

const assertEntryIsValid = (
    entry,
    expectedTitle = ENTRY_TITLE,
    expectedUsername = setupUtils.DEFAULT_SECRET_NAME,
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
        assert.isNull(entry.clearPassword);
    }
};

describe('CensysSetupUtils', () => {
    beforeEach(() => {
        fetch.resetMocks();
    });
    it('finds element by name', () => {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(
            `<feed><entry name="notTestName"></entry><entry name="testName"></entry></feed>`,
            'text/xml'
        );
        const elements = xmlDoc.getElementsByTagName('entry');
        const element = setupUtils.findElementByName('testName', elements);
        assert.isNotNull(element);
        assert.equal(element.getAttribute('name'), 'testName');
    });
    it('returns null if element not found', () => {
        const elements = [];
        const element = setupUtils.findElementByName('testName', elements);
        assert.isNull(element);
    });
    it('gets secret entries', async () => {
        fetch.mockResponseOnce(PASSWORDS_XML, {
            status: 200,
            headers: { 'Content-Type': 'text/xml' },
            url: makeUrl('storage/passwords'),
        });
        const secretEntries = await setupUtils.getSecretEntries();
        assert.equal(secretEntries.length, 1);
        const secretEntry = secretEntries[0];
        assertEntryIsValid(secretEntry);
    });
    it('error getting secret entries', async () => {
        fetch.mockResponseOnce(ERROR_XML, {
            status: 500,
            headers: { 'Content-Type': 'text/xml' },
            url: makeUrl('storage/passwords'),
        });
        await expect(setupUtils.getSecretEntries()).rejects.toThrowErrorMatchingSnapshot();
    });
    it('gets secret entry', async () => {
        fetch.mockResponseOnce(PASSWORDS_XML, {
            status: 200,
            headers: { 'Content-Type': 'text/xml' },
            url: makeUrl('storage/passwords'),
        });
        const secretEntry = await setupUtils.getSecretEntry(setupUtils.DEFAULT_SECRET_NAME);
        assertEntryIsValid(secretEntry);
    });
    it('error getting secret entry', async () => {
        fetch.mockResponseOnce(ERROR_XML, {
            status: 500,
            headers: { 'Content-Type': 'text/xml' },
            url: makeUrl('storage/passwords'),
        });
        await expect(
            setupUtils.getSecretEntry(setupUtils.DEFAULT_SECRET_NAME)
        ).rejects.toThrowErrorMatchingSnapshot();
    });
    it('creates secret entry', async () => {
        fetch.mockResponseOnce(PASSWORD_XML, {
            status: 200,
            headers: { 'Content-Type': 'text/xml' },
            url: makeUrl(`storage/passwords/${ENTRY_TITLE}`),
        });
        const secretEntry = await setupUtils.createSecretEntry(
            setupUtils.DEFAULT_SECRET_NAME,
            TEST_SECRETS
        );
        assertEntryIsValid(secretEntry, ENTRY_TITLE, setupUtils.DEFAULT_SECRET_NAME, false);
    });
    it('error creating secret entry', async () => {
        fetch.mockResponseOnce(ERROR_XML, {
            status: 404,
            headers: { 'Content-Type': 'text/xml' },
            url: makeUrl(`storage/passwords/${ENTRY_TITLE}`),
        });
        await expect(
            setupUtils.createSecretEntry(setupUtils.DEFAULT_SECRET_NAME, TEST_SECRETS)
        ).rejects.toThrowErrorMatchingSnapshot();
    });
    it('updates secret entry', async () => {
        fetch.mockResponseOnce(PASSWORD_XML, {
            status: 200,
            headers: { 'Content-Type': 'text/xml' },
            url: makeUrl(`storage/passwords/${ENTRY_TITLE}`),
        });
        const secretEntry = await setupUtils.updateSecretEntry(
            setupUtils.DEFAULT_SECRET_NAME,
            TEST_SECRETS
        );
        assertEntryIsValid(secretEntry, ENTRY_TITLE, setupUtils.DEFAULT_SECRET_NAME, false);
    });
    it('error updating secret entry', async () => {
        fetch.mockResponseOnce(ERROR_XML, {
            status: 404,
            headers: { 'Content-Type': 'text/xml' },
            url: makeUrl(`storage/passwords/${ENTRY_TITLE}`),
        });
        await expect(
            setupUtils.updateSecretEntry(setupUtils.DEFAULT_SECRET_NAME, TEST_SECRETS)
        ).rejects.toThrowErrorMatchingSnapshot();
    });
});
