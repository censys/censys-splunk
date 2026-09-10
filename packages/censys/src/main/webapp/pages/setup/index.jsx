import React from 'react';

import layout from '@splunk/react-page';
import { getThemeOptions } from '@splunk/splunk-utils/themes';
import { SplunkThemeProvider } from '@splunk/themes';

import CensysSetup from '@splunk/censys-setup';

import injectAppStyles from '../../appStyles';

const themeProviderSettings = getThemeOptions('enterprise');

injectAppStyles();

layout(
    <SplunkThemeProvider {...themeProviderSettings}>
        <CensysSetup />
    </SplunkThemeProvider>,
    { pageTitle: 'Censys Setup' }
);
