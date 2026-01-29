/* eslint-env jest */
import { assert } from 'chai';
import Enzyme, { mount } from 'enzyme';
import EnzymeAdapterReact16 from 'enzyme-adapter-react-16';
import React from 'react';

import CensysInputs from '../CensysInputs';

// Mock @splunk/censys-utils so no real fetch runs (avoids "Only absolute URLs are supported" in Jest)
jest.mock('@splunk/censys-utils', () => {
    const ASM_RISKS_INPUT_TYPE = 'censys_asm_risks';
    const ASM_LOGBOOK_INPUT_TYPE = 'censys_asm_logbook';
    return {
        defaultApp: 'Splunk_TA_censys',
        inputs: {
            ASM_RISKS_INPUT_TYPE,
            ASM_LOGBOOK_INPUT_TYPE,
            inputTypeNames: {
                [ASM_RISKS_INPUT_TYPE]: 'Censys ASM Risks',
                [ASM_LOGBOOK_INPUT_TYPE]: 'Censys ASM Logbook',
            },
            getInputs: jest.fn().mockResolvedValue([]),
            getIndexes: jest.fn().mockResolvedValue(['main', 'security']),
            createInput: jest.fn().mockResolvedValue(undefined),
            updateInput: jest.fn().mockResolvedValue(undefined),
            setDisabledStatus: jest.fn().mockResolvedValue(undefined),
        },
    };
});

// This sets up the enzyme adapter
const adapter = new EnzymeAdapterReact16();
Enzyme.configure({ adapter });

describe('CensysInputs', () => {
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
