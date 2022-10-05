/* eslint-env jest */
import { assert } from 'chai';
import Enzyme, { mount } from 'enzyme';
import EnzymeAdapterReact16 from 'enzyme-adapter-react-16';
import React from 'react';

import GearIcon from '@splunk/react-icons/Gear';

import CensysGettingStarted from '../CensysGettingStarted';

// This sets up the enzyme adapter
const adapter = new EnzymeAdapterReact16();
Enzyme.configure({ adapter });

const defaultProps = {
    appLabel: 'Censys',
};

describe('CensysGettingStarted', () => {
    it('renders with custom name', () => {
        const wrapper = mount(<CensysGettingStarted {...defaultProps} />);
        assert.include(wrapper.text(), `Welcome to ${defaultProps.appLabel}!`);
        wrapper.unmount();
    });

    it('renders with custom message', () => {
        const message = {
            type: 'warning',
            content: 'Your app needs an update',
        };
        const wrapper = mount(<CensysGettingStarted {...defaultProps} message={message} />);
        assert.include(wrapper.text(), message.content);
        wrapper.unmount();
    });

    it('renders with custom tasks', () => {
        const tasks = [
            {
                title: 'Setup your Censys credentials',
                description: 'Configure your Censys credentials in the Censys for Splunk app.',
                icon: GearIcon,
                path: '/setup',
            },
        ];
        const wrapper = mount(<CensysGettingStarted {...defaultProps} tasks={tasks} />);
        assert.include(wrapper.text(), tasks[0].title);
        assert.include(wrapper.text(), tasks[0].description);
        wrapper.unmount();
    });
});
