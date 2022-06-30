import React from 'react';

import layout from '@splunk/react-page';
import { defaultTheme, getThemeOptions } from '@splunk/splunk-utils/themes';
import { SplunkThemeProvider } from '@splunk/themes';

import CensysGettingStarted from '@splunk/censys-getting-started';

const themeProviderSettings = getThemeOptions(defaultTheme() || 'enterprise');

layout(
    <SplunkThemeProvider {...themeProviderSettings}>
        <CensysGettingStarted />
    </SplunkThemeProvider>,
    { pageTitle: 'Censys Getting Started' }
);
