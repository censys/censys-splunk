import fetch from 'cross-fetch';
import React, { useEffect, useState } from 'react';

import BellIcon from '@splunk/react-icons/Bell';
import DataInputIcon from '@splunk/react-icons/DataInput';
import GearIcon from '@splunk/react-icons/Gear';
import ReportPivotIcon from '@splunk/react-icons/ReportPivot';
import ReportSearchIcon from '@splunk/react-icons/ReportSearch';
import SearchIcon from '@splunk/react-icons/Search';
import layout from '@splunk/react-page';
import { defaultFetchInit } from '@splunk/splunk-utils/fetch';
import { defaultTheme, getThemeOptions } from '@splunk/splunk-utils/themes';
import { createRESTURL } from '@splunk/splunk-utils/url';
import { SplunkThemeProvider } from '@splunk/themes';

import CensysGettingStarted from '@splunk/censys-getting-started';

const themeProviderSettings = getThemeOptions(defaultTheme() || 'enterprise');

const getLocalApps = (signal = null) => {
    return fetch(
        createRESTURL(
            'apps/local?output_mode=json&sort_key=name&sort_dir=asc&search=visible%3Dtrue%20AND%20disabled%3D0&count=-1',
            {
                owner: 'admin',
            }
        ),
        { ...defaultFetchInit, signal }
    )
        .then((response) => response.json())
        .then((data) => data.entry);
};

const isAppConfigured = (app) => app.content.configured;

const footerLinks = [
    {
        title: 'Documentation',
        // TODO: Add link to documentation
        href: '',
    },
    {
        title: 'Support',
        // TODO: Update link to support
        href: 'https://support.censys.io/hc/en-us/articles/360059326151-Censys-ASM-for-Splunk',
    },
];

const CensysAppGettingStarted = () => {
    const [appStates, setAppStates] = useState({
        addOnInstalled: false,
        addOnConfigured: false,
        appConfigured: false,
    });

    useEffect(() => {
        const controller = new AbortController();
        getLocalApps(controller.signal).then((apps) => {
            if (apps.length > 0) {
                const addOn = apps.find((appEntry) => appEntry.name === 'Splunk_TA_censys');
                const app = apps.find((appEntry) => appEntry.name === 'censys');
                setAppStates({
                    addOnInstalled: addOn !== undefined,
                    addOnConfigured: addOn !== undefined && isAppConfigured(addOn),
                    appConfigured: app !== undefined && isAppConfigured(app),
                });
            }
        });
        return () => controller?.abort();
    }, []);

    const { addOnInstalled, addOnConfigured, appConfigured } = appStates;

    const tasks = [
        // Keep descriptions less than 50 characters
        {
            title: 'Setup your Censys credentials',
            description: 'Configure your credentials to unlock all the features.',
            icon: GearIcon,
            path: '/setup',
            show: !appConfigured,
        },
        {
            title: 'Install the Censys Add-on',
            description: 'Install the Censys Add-on to access the Censys API.',
            icon: DataInputIcon,
            path: '/manager/censys/appsremote?offset=0&count=20&order=relevance&query=Censys%20Add-on%20for%20Splunk',
            show: !addOnInstalled,
        },
        {
            title: 'Setup the Censys Add-on',
            description: 'Configure your credentials.',
            icon: DataInputIcon,
            path: '/app/Splunk_TA_censys/setup',
            show: !addOnConfigured,
        },
        {
            title: 'Setup Censys Add-on Inputs',
            description: 'Configure your data input to ingest your data.',
            icon: DataInputIcon,
            path: '/app/Splunk_TA_censys/inputs',
            show: addOnConfigured,
        },
        {
            title: 'Write your first search',
            description: 'Get started with an example search.',
            icon: SearchIcon,
            path: '/search?q=search%20sourcetype%3D%22censys%3Aasm%3A*%22&earliest=-30d%40d&latest=now',
        },
        {
            title: 'Create a report',
            description: 'View pre-built reports and create your own.',
            icon: ReportSearchIcon,
            path: '/reports',
        },
        {
            title: 'Create alerts',
            description: 'Setup alerts when your search results change.',
            icon: BellIcon,
            path: '/alerts',
        },
        {
            title: 'Use Workflow Actions',
            description: 'Level up your investigation with the Workflow Actions.',
            icon: ReportPivotIcon,
            modal: {
                header: 'Workflow Actions',
                content: (
                    <div>
                        <p>Workflow Actions are a powerful way to automate your Splunk search.</p>
                    </div>
                ),
                image: 'workflow-actions.png',
            },
        },
    ];

    return <CensysGettingStarted appLabel="Censys for Splunk" tasks={tasks} links={footerLinks} />;
};

layout(
    <SplunkThemeProvider {...themeProviderSettings}>
        <CensysAppGettingStarted />
    </SplunkThemeProvider>,
    { pageTitle: 'Censys Getting Started' }
);
