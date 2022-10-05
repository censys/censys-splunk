import React from 'react';

import DataInputIcon from '@splunk/react-icons/DataInput';
import GearIcon from '@splunk/react-icons/Gear';
import SearchIcon from '@splunk/react-icons/Search';
import layout from '@splunk/react-page';
import { defaultTheme, getThemeOptions } from '@splunk/splunk-utils/themes';
import { SplunkThemeProvider } from '@splunk/themes';

import CensysGettingStarted from '@splunk/censys-getting-started';

const themeProviderSettings = getThemeOptions(defaultTheme() || 'enterprise');

const tasks = [
    {
        // TODO: Only show setup task if the user is not logged in
        title: 'Setup your Censys credentials',
        description: 'Configure your credentials to unlock all the features.',
        icon: GearIcon,
        path: '/setup',
    },
    {
        title: 'Setup Censys Add-on Inputs',
        description: 'Configure your data input to ingest your data.',
        icon: DataInputIcon,
        path: '/app/Splunk_TA_censys/inputs',
    },
    {
        title: 'Write your first search',
        description: 'Get started with an example search.',
        icon: SearchIcon,
        path: '/search?q=search%20sourcetype%3D%22censys%3Aasm%3A*%22&earliest=-30d%40d&latest=now',
    },
];

const CensysAddonGettingStarted = () => {
    return <CensysGettingStarted appLabel="Censys Add-on for Splunk" tasks={tasks} />;
};

layout(
    <SplunkThemeProvider {...themeProviderSettings}>
        <CensysAddonGettingStarted />
    </SplunkThemeProvider>,
    { pageTitle: 'Censys Add-on Getting Started' }
);
