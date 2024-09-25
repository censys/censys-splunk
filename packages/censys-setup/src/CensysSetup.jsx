import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import Button from '@splunk/react-ui/Button';
import ControlGroup from '@splunk/react-ui/ControlGroup';
import Heading from '@splunk/react-ui/Heading';
import Link from '@splunk/react-ui/Link';
import MessageBar from '@splunk/react-ui/MessageBar';
import Text from '@splunk/react-ui/Text';

import { api, defaultApp, secrets } from '@splunk/censys-utils';

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

const CensysSetup = ({ appId, title }) => {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    const [formErrors, setFormErrors] = useState({
        asmApiKey: '',
    });
    const [secretExists, setSecretExists] = useState(true);
    const [asmApiKey, setAsmApiKey] = useState('');

    const appPath = `/app/${appId}`;
    const startPath = `${appPath}/start`;

    const asmError = formErrors.asmApiKey;

    const asmHelp = (
        <span>
            Get your API key from the
            <Link to="https://app.censys.io/integrations" openInNewContext>
                ASM integrations page
            </Link>
            {asmError && <p>{asmError}</p>}
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
            const asmApiKeyValid = asmApiKey.match(secrets.ASM_API_KEY_REGEX);
            errors.asmApiKey = asmApiKeyValid ? '' : 'Invalid ASM API key.';
        } else {
            errors.asmApiKey = '';
        }

        if (!asmApiKey) {
            errors.asmApiKey = 'Invalid ASM API key.';
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
        const newSecrets = {
            censys_asm_api_key: asmApiKey,
        };
        try {
            // If the secret exists, update it otherwise create it
            if (secretExists) {
                await secrets.updateSecretEntry(secrets.DEFAULT_SECRET_NAME, newSecrets);
            } else {
                await secrets.createSecretEntry(secrets.DEFAULT_SECRET_NAME, newSecrets);
            }

            // Set the app to configured
            await api.setIsConfigured(true);
            await api.reloadApp();
            setFormErrors({});
            setMessage({ type: 'success', content: successMessage });
        } catch (error) {
            setMessage({ type: 'warning', content: error.toString() });
        }
        setLoading(false);
    };

    useEffect(() => {
        let controller = new AbortController();
        secrets
            .getSecretEntry(secrets.DEFAULT_SECRET_NAME, controller.signal)
            .then((secretEntry) => {
                const clearSecrets = secretEntry.clearPassword;
                if (clearSecrets) {
                    const censysAsmApiKey = clearSecrets.censys_asm_api_key;
                    if (censysAsmApiKey) {
                        setAsmApiKey(censysAsmApiKey);
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
                {title}
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

            <Button label="Submit" appearance="primary" disabled={loading} onClick={handleSubmit} />
        </div>
    );
};
CensysSetup.propTypes = {
    appId: PropTypes.string,
    title: PropTypes.string,
};
CensysSetup.defaultProps = {
    appId: defaultApp,
    title: 'Censys Setup',
};

export default CensysSetup;
