import PropTypes from 'prop-types';
import React, { useState } from 'react';

import Card from '@splunk/react-ui/Card';
import CardLayout from '@splunk/react-ui/CardLayout';
import Heading from '@splunk/react-ui/Heading';
import Link from '@splunk/react-ui/Link';
import MessageBar from '@splunk/react-ui/MessageBar';
import Modal from '@splunk/react-ui/Modal';
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
const CARD_STYLE = { minWidth: '350px', maxWidth: '350px', margin: '0 20px 20px 0' };
const LINK_STYLE = {
    margin: '0 20px 0 0',
};

const CensysGettingStarted = ({ appId, appLabel, message, tasks, links }) => {
    const appPath = `/app/${appId}`;

    const [showModal, setShowModal] = useState(false);
    const [modalPage, setModalPage] = useState(null);

    const handleRequestClose = () => {
        setShowModal(false);
    };

    return (
        <div className="section-padded section-header">
            <Heading level={1} className="section-title search-title-searchname">
                Welcome to {appLabel}!
            </Heading>
            {message && <MessageBar type={message.type}>{message.content}</MessageBar>}
            {tasks && (
                <CardLayout style={CARD_LAYOUT_STYLE}>
                    {tasks
                        .filter((task) => task.show === undefined || task.show)
                        .map(({ title, description, icon, path, modal }, index) => {
                            const colorIndex = index % COLOR_OPTIONS.length;
                            const cardBodyStyle = {
                                textAlign: 'center',
                                color: COLOR_OPTIONS[colorIndex],
                                background: BACKGROUND_COLOR_OPTIONS[colorIndex],
                            };
                            const Icon = icon;
                            const cardProps = {
                                style: CARD_STYLE,
                                key: title.toLowerCase().replace(' ', '-'),
                            };
                            if (path) {
                                if (
                                    path.startsWith('/') &&
                                    !path.startsWith('/app/') &&
                                    !path.startsWith('/manager/')
                                ) {
                                    cardProps.to = `${appPath}${path}`;
                                } else {
                                    cardProps.to = path;
                                }
                            }
                            if (modal) {
                                cardProps.onClick = () => {
                                    setModalPage(modal);
                                    setShowModal(true);
                                };
                            }
                            return (
                                <Card {...cardProps}>
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
                        openInNewContext={true}
                    >
                        {title}
                    </Link>
                ))}
            {modalPage && (
                <Modal
                    style={{ width: '600px' }}
                    open={showModal}
                    onRequestClose={handleRequestClose}
                >
                    <Modal.Header title={modalPage.header} onRequestClose={handleRequestClose} />
                    <Modal.Body>
                        {modalPage.content}
                        {modalPage.image && (
                            <img
                                src={`/static${appPath}/${modalPage.image}`}
                                style={{ width: '100%' }}
                                alt={modalPage.header}
                            />
                        )}
                    </Modal.Body>
                </Modal>
            )}
        </div>
    );
};
CensysGettingStarted.propTypes = {
    appId: PropTypes.string,
    appLabel: PropTypes.string.isRequired,
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
            modal: PropTypes.shape({
                header: PropTypes.string,
                content: PropTypes.element,
                image: PropTypes.string,
            }),
            show: PropTypes.bool,
        }).isRequired
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
    // message: {
    //     content: 'Your app needs an update',
    //     type: 'warning',
    // },
};
export default CensysGettingStarted;
