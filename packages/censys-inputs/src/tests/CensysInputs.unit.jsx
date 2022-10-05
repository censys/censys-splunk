/* eslint-env jest */
import { assert } from 'chai';
import Enzyme, { mount } from 'enzyme';
import EnzymeAdapterReact16 from 'enzyme-adapter-react-16';
import React from 'react';

// import { inputs } from '@splunk/censys-utils';
import CensysInputs from '../CensysInputs';

// This sets up the enzyme adapter
const adapter = new EnzymeAdapterReact16();
Enzyme.configure({ adapter });

// Mock the inputs module
// jest.mock('@splunk/censys-utils');

describe('CensysInputs', () => {
    // beforeAll(() => {
    //     inputs.getInputs = jest.fn().mockResolvedValue([
    //         {
    //             name: 'smoke_test_risks',
    //             type: inputs.ASM_RISKS_INPUT_TYPE,
    //             interval: 3600,
    //             index: 'main',
    //             authentication: 'Global',
    //             status: true,
    //             selected: false,
    //         },
    //         {
    //             name: 'smoke_test_logbook',
    //             type: inputs.ASM_LOGBOOK_INPUT_TYPE,
    //             interval: 3600,
    //             index: 'main',
    //             authentication: 'Global',
    //             status: true,
    //             selected: false,
    //         },
    //     ]);
    // });

    it('renders with default title', () => {
        const wrapper = mount(<CensysInputs />);
        assert.include(wrapper.text(), 'Censys Inputs');
        wrapper.unmount();
    });

    it('renders with custom title', () => {
        const title = 'Censys Inputs';
        const wrapper = mount(<CensysInputs title={title} />);
        assert.include(wrapper.text(), title);
        wrapper.unmount();
    });
});
