import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import Button from '@splunk/react-ui/Button';
import ControlGroup from '@splunk/react-ui/ControlGroup';
import Heading from '@splunk/react-ui/Heading';
import Link from '@splunk/react-ui/Link';
import MessageBar from '@splunk/react-ui/MessageBar';
import Text from '@splunk/react-ui/Text';
import * as config from '@splunk/splunk-utils/config';
import { variables } from '@splunk/themes';

import {
    ASM_API_KEY_REGEX,
    DEFAULT_APP,
    DEFAULT_SECRET_NAME,
    SEARCH_API_ID_REGEX,
    SEARCH_API_SECRET_REGEX,
    createSecretEntry,
    getSecretEntry,
    reloadApp,
    setIsConfigured,
    updateSecretEntry,
} from './CensysSetupUtils';

const inputStyle = {
    height: '32px',
};
const inputProp = {
    autoComplete: 'new-password',
    autoCapitalize: 'off',
    spellCheck: false,
    passwordVisibilityToggle: true,
    className: 'splunk-input-container',
};

const isEmpty = (str) => {
    return !str || str.length === 0;
};

const CensysSetup = ({ appId }) => {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [formErrors, setFormErrors] = useState({
        asmApiKey: '',
        searchAppId: '',
        searchAppSecret: '',
    });
    const [secretExists, setSecretExists] = useState(true);
    const [asmApiKey, setAsmApiKey] = useState('');
    const [searchAppId, setSearchAppId] = useState('');
    const [searchAppSecret, setSearchAppSecret] = useState('');

    const appPath = `/app/${appId}`;
    const startPath = `${appPath}/start`;

    const asmError = formErrors.asmApiKey;
    const searchError = formErrors.searchAppId || formErrors.searchAppSecret;
    const searchErrors = [formErrors.searchAppId, formErrors.searchAppSecret].filter(
        (error) => error !== ''
    );

    const asmHelp = (
        <span>
            Get your API key from the{' '}
            <Link to="https://app.censys.io/integrations" openInNewContext>
                ASM integrations page
            </Link>
            {asmError && <p>{asmError}</p>}
        </span>
    );

    const searchHelp = (
        <span>
            Get your API key from the{' '}
            <Link to="https://search.censys.io/account/api" openInNewContext>
                Search account page
            </Link>
            {searchError && <p>{searchErrors.join(' ')}</p>}
        </span>
    );

    const successMessage = (
        <span>
            Your Censys app is configured. Let&apos;s <Link to={startPath}>Get Started!</Link>
        </span>
    );

    const handleValidation = () => {
        const errors = {};

        if (asmApiKey) {
            const asmApiKeyValid = asmApiKey.match(ASM_API_KEY_REGEX);
            errors.asmApiKey = asmApiKeyValid ? '' : 'Invalid ASM API key.';
        } else {
            errors.asmApiKey = '';
        }

        if (searchAppId || searchAppSecret) {
            const searchAppIdValid = searchAppId.match(SEARCH_API_ID_REGEX);
            const searchAppSecretValid = searchAppSecret.match(SEARCH_API_SECRET_REGEX);
            errors.searchAppId = searchAppIdValid ? '' : 'Invalid Search App ID.';
            errors.searchAppSecret = searchAppSecretValid ? '' : 'Invalid Search App Secret.';
        } else {
            errors.searchAppId = '';
            errors.searchAppSecret = '';
        }

        if (!asmApiKey && !searchAppId && !searchAppSecret) {
            errors.asmApiKey = 'Invalid ASM API key.';
            errors.searchAppId = 'Invalid Search App ID.';
            errors.searchAppSecret = 'Invalid Search App Secret.';
        }

        return errors;
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const errors = handleValidation();
        if (Object.values(errors).some((error) => error !== '')) {
            setFormErrors({ ...formErrors, ...errors });
            return;
        }
        setLoading(true);
        const secrets = {
            censys_asm_api_key: asmApiKey,
            censys_search_app_id: searchAppId,
            censys_search_app_secret: searchAppSecret,
        };
        try {
            // If the secret exists, update it otherwise create it
            if (secretExists) {
                await updateSecretEntry(DEFAULT_SECRET_NAME, secrets);
            } else {
                await createSecretEntry(DEFAULT_SECRET_NAME, secrets);
            }

            // Set the app to configured
            await setIsConfigured(true);
            await reloadApp();
            setFormErrors({});
            setMessage({ type: 'success', content: successMessage });
        } catch (error) {
            setMessage({ type: 'warning', content: error.toString() });
        }
        setLoading(false);
    };

    useEffect(() => {
        let controller = new AbortController();
        getSecretEntry(DEFAULT_SECRET_NAME, controller.signal)
            .then((secretEntry) => {
                const clearSecrets = secretEntry.clearPassword;
                if (clearSecrets) {
                    const censysAsmApiKey = clearSecrets.censys_asm_api_key;
                    const censysSearchAppId = clearSecrets.censys_search_app_id;
                    const censysSearchAppSecret = clearSecrets.censys_search_app_secret;
                    if (censysAsmApiKey) {
                        setAsmApiKey(censysAsmApiKey);
                    }
                    if (censysSearchAppId) {
                        setSearchAppId(censysSearchAppId);
                    }
                    if (censysSearchAppSecret) {
                        setSearchAppSecret(censysSearchAppSecret);
                    }
                }
                controller = null;
            })
            .catch(() => {
                setSecretExists(false);
            });
        return () => controller?.abort();
    }, []);

    return (
        <div className="section-padded section-header">
            <Heading level={1} className="section-title search-title-searchname">
                Censys Setup
            </Heading>

            {message && <MessageBar type={message.type || 'info'}>{message.content}</MessageBar>}

            <ControlGroup
                label="Censys ASM"
                labelPosition="top"
                help={asmHelp}
                error={!isEmpty(formErrors.asmApiKey)}
            >
                <Text
                    placeholder="Your ASM API Key"
                    maxLength={36}
                    value={asmApiKey}
                    onChange={(e) => setAsmApiKey(e.target.value)}
                    style={inputStyle}
                    error={!isEmpty(formErrors.asmApiKey)}
                    {...inputProp}
                />
            </ControlGroup>

            <ControlGroup
                label="Censys Search"
                labelPosition="top"
                help={searchHelp}
                error={!isEmpty(formErrors.searchAppId || formErrors.searchAppSecret)}
            >
                <Text
                    placeholder="Your Search API ID"
                    maxLength={36}
                    value={searchAppId}
                    onChange={(e) => setSearchAppId(e.target.value)}
                    style={{ ...inputStyle, marginRight: variables.spacingQuarter }}
                    error={!isEmpty(formErrors.searchAppId)}
                    {...inputProp}
                />
                <Text
                    placeholder="Your Search API Secret"
                    maxLength={32}
                    value={searchAppSecret}
                    onChange={(e) => setSearchAppSecret(e.target.value)}
                    style={inputStyle}
                    error={!isEmpty(formErrors.searchAppSecret)}
                    {...inputProp}
                />
            </ControlGroup>
            <Button label="Submit" appearance="primary" disabled={loading} onClick={handleSubmit} />
        </div>
    );
};
CensysSetup.propTypes = {
    appId: PropTypes.string,
};
CensysSetup.defaultProps = {
    appId: config.app || DEFAULT_APP,
};

export default CensysSetup;
