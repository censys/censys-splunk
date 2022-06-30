import { enableFetchMocks } from 'jest-fetch-mock';
import enableHooks from 'jest-react-hooks-shallow';

// Enable fetch mocks
enableFetchMocks();
jest.setMock('cross-fetch', fetchMock);

// Enable jest hooks
enableHooks(jest, { dontMockByDefault: true });
