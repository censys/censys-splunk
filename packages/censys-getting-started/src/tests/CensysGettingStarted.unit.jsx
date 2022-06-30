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

describe('CensysGettingStarted', () => {
    it('renders with default name', () => {
        const wrapper = mount(<CensysGettingStarted />);
        assert.include(wrapper.text(), 'Welcome to Censys for Splunk!');
        wrapper.unmount();
    });

    it('renders with custom name', () => {
        const appLabel = 'Censys';
        const wrapper = mount(<CensysGettingStarted appLabel={appLabel} />);
        assert.include(wrapper.text(), `Welcome to ${appLabel}!`);
        wrapper.unmount();
    });

    it('renders with custom message', () => {
        const message = {
            type: 'warning',
            content: 'Your app needs an update',
        };
        const wrapper = mount(<CensysGettingStarted message={message} />);
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
        const wrapper = mount(<CensysGettingStarted tasks={tasks} />);
        assert.include(wrapper.text(), tasks[0].title);
        assert.include(wrapper.text(), tasks[0].description);
        wrapper.unmount();
    });
});
