import React from 'react';

import layout from '@splunk/react-page';
import { defaultTheme, getThemeOptions } from '@splunk/splunk-utils/themes';
import { SplunkThemeProvider } from '@splunk/themes';

import CensysSetup from '@splunk/censys-setup';

const themeProviderSettings = getThemeOptions(defaultTheme() || 'enterprise');

layout(
    <SplunkThemeProvider {...themeProviderSettings}>
        <CensysSetup />
    </SplunkThemeProvider>,
    { pageTitle: 'Censys Setup' }
);