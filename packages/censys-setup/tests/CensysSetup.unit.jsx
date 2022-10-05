/* eslint-env jest */
import { assert } from 'chai';
import Enzyme, { mount } from 'enzyme';
import EnzymeAdapterReact16 from 'enzyme-adapter-react-16';
import React from 'react';

import CensysSetup from '../src/CensysSetup';

// This sets up the enzyme adapter
const adapter = new EnzymeAdapterReact16();
Enzyme.configure({ adapter });

describe('CensysSetup', () => {
    // beforeAll(() => {
    //     secrets.getSecretEntry.mockResolvedValue({
    //         clearPassword: {
    //             censys_asm_api_key: 'censys_asm_api_key',
    //             censys_search_app_id: 'censys_search_app_id',
    //             censys_search_app_secret: 'censys_search_app_secret',
    //         },
    //     });
    // });

    it('renders with default title', () => {
        const wrapper = mount(<CensysSetup />);
        assert.include(wrapper.text(), 'Censys Setup', "Default title is 'Censys Setup'");
        wrapper.unmount();
    });

    it('renders with custom title', () => {
        const title = 'Censys App Setup';
        const wrapper = mount(<CensysSetup title={title} />);
        assert.include(wrapper.text(), title, "Title doesn't match");
        wrapper.unmount();
    });

    // TODO: Fix mocking of secrets useEffect calls
    // it('renders with custom message', () => {
    //     const message = {
    //         type: 'warning',
    //         content: 'Your app needs an update',
    //     };
    //     const wrapper = mount(<CensysSetup message={message} />);
    //     assert.include(wrapper.text(), message.content, "Message doesn't match");
    //     wrapper.unmount();
    // });
});
