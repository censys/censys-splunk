import { enableFetchMocks } from 'jest-fetch-mock';

// Enable fetch mocks
enableFetchMocks();
jest.setMock('cross-fetch', fetchMock);
