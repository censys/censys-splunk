import React from 'react';
import { render } from 'react-dom';

import { defaultTheme, getThemeOptions } from '@splunk/splunk-utils/themes';
import { SplunkThemeProvider } from '@splunk/themes';

import CensysSetup from '../src/CensysSetup';

const themeProviderSettings = getThemeOptions(defaultTheme() || 'enterprise');

const containerEl = document.getElementById('main-component-container');
render(
    <SplunkThemeProvider {...themeProviderSettings}>
        <CensysSetup />
    </SplunkThemeProvider>,
    containerEl
);
