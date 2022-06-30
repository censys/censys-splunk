import PropTypes from 'prop-types';
import React from 'react';

import BellIcon from '@splunk/react-icons/Bell';
import GearIcon from '@splunk/react-icons/Gear';
import ReportPivotIcon from '@splunk/react-icons/ReportPivot';
import ReportSearchIcon from '@splunk/react-icons/ReportSearch';
import SearchIcon from '@splunk/react-icons/Search';
import Card from '@splunk/react-ui/Card';
import CardLayout from '@splunk/react-ui/CardLayout';
import Heading from '@splunk/react-ui/Heading';
import Link from '@splunk/react-ui/Link';
import MessageBar from '@splunk/react-ui/MessageBar';
import * as config from '@splunk/splunk-utils/config';

const COLOR_OPTIONS = ['#ff5200', '#3a87ad', '#65a637', '#f8be34'];
const BACKGROUND_COLOR_OPTIONS = ['#ffbb9b', '#d9edf7', '#d0e9be', '#ffeeae'];

const ICON_SIZE = '150px';
const ICON_STYLE = {
    width: ICON_SIZE,
    height: ICON_SIZE,
    padding: '30px',
};
const CARD_LAYOUT_STYLE = {
    padding: 0,
};
const CARD_STYLE = { minWidth: '300px', margin: '0 20px 20px 0' };
const LINK_STYLE = {
    margin: '0 20px 0 0',
};

const CensysGettingStarted = ({ appId, appLabel, message, tasks, links }) => {
    const appPath = `/app/${appId}`;
    return (
        <div className="section-padded section-header">
            <Heading level={1} className="section-title search-title-searchname">
                Welcome to {appLabel}!
            </Heading>
            {message && <MessageBar type={message.type}>{message.content}</MessageBar>}
            {tasks && (
                <CardLayout style={CARD_LAYOUT_STYLE}>
                    {tasks.map(({ title, description, icon, path }, index) => {
                        const colorIndex = index % COLOR_OPTIONS.length;
                        const cardBodyStyle = {
                            textAlign: 'center',
                            color: COLOR_OPTIONS[colorIndex],
                            background: BACKGROUND_COLOR_OPTIONS[colorIndex],
                        };
                        const Icon = icon;
                        return (
                            <Card
                                style={CARD_STYLE}
                                to={appPath + path}
                                key={title.toLowerCase().replace(' ', '-')}
                            >
                                <Card.Header title={title} subtitle={description} />
                                <Card.Body style={cardBodyStyle}>
                                    <Icon style={ICON_STYLE} />
                                </Card.Body>
                            </Card>
                        );
                    })}
                </CardLayout>
            )}
            {links &&
                links.map(({ title, path }) => (
                    <Link
                        style={LINK_STYLE}
                        to={path}
                        key={title.toLowerCase().replace(' ', '-')}
                        openInNewContext
                    >
                        {title}
                    </Link>
                ))}
        </div>
    );
};
CensysGettingStarted.propTypes = {
    appId: PropTypes.string,
    appLabel: PropTypes.string,
    message: PropTypes.shape({
        content: PropTypes.string,
        type: PropTypes.string,
    }),
    tasks: PropTypes.arrayOf(
        PropTypes.shape({
            title: PropTypes.string,
            description: PropTypes.string,
            icon: PropTypes.func,
            path: PropTypes.string,
            func: PropTypes.func,
        })
    ),
    links: PropTypes.arrayOf(
        PropTypes.shape({
            title: PropTypes.string,
            path: PropTypes.string,
        })
    ),
};
CensysGettingStarted.defaultProps = {
    appId: config.app || 'censys',
    appLabel: 'Censys for Splunk',
    tasks: [
        // Keep descriptions less than 50 characters
        {
            // TODO: Only show setup task if the user is not logged in
            title: 'Setup your Censys credentials',
            description: 'Configure your credentials to unlock all the features.',
            icon: GearIcon,
            path: '/setup',
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
            path: '/search',
        },
    ],
    links: [
        {
            title: 'Documentation',
            href: '',
        },
        {
            title: 'Support',
            href: '',
        },
    ],
    // message: {
    //     content: 'Your app needs an update',
    //     type: 'warning',
    // },
};
export default CensysGettingStarted;
