import styled from 'styled-components';

import { mixins, variables } from '@splunk/themes';

const StyledContainer = styled.div`
    ${mixins.reset('inline-block')};
    font-size: ${variables.fontSizeLarge};
    line-height: 200%;
    height: 100%;
    width: 100%;
    margin: 0;
    background-color: ${variables.gray96};
`;

export { StyledContainer };
