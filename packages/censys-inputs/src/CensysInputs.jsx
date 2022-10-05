import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import Button from '@splunk/react-ui/Button';
import Dropdown from '@splunk/react-ui/Dropdown';
import Heading from '@splunk/react-ui/Heading';
import Menu from '@splunk/react-ui/Menu';
import P from '@splunk/react-ui/Paragraph';
import WaitSpinner from '@splunk/react-ui/WaitSpinner';

import { defaultApp, inputs } from '@splunk/censys-utils';

import InputModal, { InputModalMode } from './InputModal';
import InputsTable from './InputsTable';

const DEFAULT_INPUT_TYPE = inputs.ASM_RISKS_INPUT_TYPE;

const CensysInputs = ({ title }) => {
    const [loading, setLoading] = useState(true);
    const [refreshInputs, setRefreshInputs] = useState(0);
    const [censysInputs, setCensysInputs] = useState([]);
    const [inputTypeTpCreate, setInputTypeToCreate] = useState(DEFAULT_INPUT_TYPE);
    const [inputToEdit, setInputToEdit] = useState(null);
    const [modalMode, setModalMode] = useState(InputModalMode.create);
    const [modalOpen, setModalOpen] = useState(false);

    const fetchInputs = async (signal = null) => {
        const risksInputs = await inputs.getInputs(DEFAULT_INPUT_TYPE, defaultApp, signal);
        const logbookInputs = await inputs.getInputs(
            inputs.ASM_LOGBOOK_INPUT_TYPE,
            defaultApp,
            signal
        );
        setCensysInputs([...logbookInputs, ...risksInputs]);
        setLoading(false);
    };

    useEffect(() => {
        const controller = new AbortController();
        fetchInputs(controller.signal);
        return () => controller?.abort();
    }, [refreshInputs]);

    const getInputWithName = (name) => censysInputs.find((input) => input.name === name);

    const closeModal = () => {
        setModalOpen(false);
        setRefreshInputs(refreshInputs + 1);
        setInputTypeToCreate(DEFAULT_INPUT_TYPE);
        setInputToEdit(null);
        setModalMode(InputModalMode.create);
    };

    const openEditModal = (input) => {
        setInputTypeToCreate(input.type);
        setInputToEdit(input);
        setModalMode(InputModalMode.edit);
        setModalOpen(true);
    };

    const handleEdit = (e, { value }) => {
        openEditModal(getInputWithName(value));
    };

    const openCloneModal = (input) => {
        setInputToEdit({ ...input, name: '' });
        setModalMode(InputModalMode.clone);
        setModalOpen(true);
    };

    const handleClone = (e, { value }) => {
        openCloneModal(getInputWithName(value));
    };

    const openDeleteModal = (input) => {
        setInputToEdit(input);
        setModalMode(InputModalMode.delete);
        setModalOpen(true);
    };

    const handleDelete = (e, { value }) => {
        openDeleteModal(getInputWithName(value));
    };

    const handleToggleStatus = (e, { value, selected }) => {
        const inputToDisable = getInputWithName(value);
        inputs.setDisabledStatus(inputToDisable.name, inputToDisable.type, selected);
        setRefreshInputs(refreshInputs + 1);
    };

    const openCreateModal = (inputType) => {
        setInputToEdit(null);
        setInputTypeToCreate(inputType);
        setModalMode(InputModalMode.create);
        setModalOpen(true);
    };

    const CreateInputMenu = () => {
        return (
            <Dropdown
                toggle={
                    <Button
                        isMenu
                        appearance="primary"
                        label="Create New Input"
                        style={{ alignContent: 'right', marginBottom: '30px', width: '160px' }}
                    />
                }
            >
                <Menu style={{ width: 160 }}>
                    <Menu.Item onClick={() => openCreateModal(inputs.ASM_RISKS_INPUT_TYPE)}>
                        Censys ASM Risks
                    </Menu.Item>
                    <Menu.Item onClick={() => openCreateModal(inputs.ASM_LOGBOOK_INPUT_TYPE)}>
                        Censys ASM Logbook
                    </Menu.Item>
                </Menu>
            </Dropdown>
        );
    };

    return (
        <div className="section-padded section-header">
            <Heading level={1} className="section-title search-title-searchname">
                {title}
            </Heading>
            {/* TODO: Fix out styling for input button */}
            <CreateInputMenu />
            <P>{censysInputs.length} inputs</P>
            {/* TODO: Add per page dropdown */}
            {/* TODO: Add input type dropdown */}
            <InputsTable
                inputsData={censysInputs}
                onEdit={handleEdit}
                onClone={handleClone}
                onDelete={handleDelete}
                onToggleStatus={handleToggleStatus}
            />
            {loading && <WaitSpinner size="large" />}
            <InputModal
                isOpen={modalOpen}
                onClose={closeModal}
                mode={modalMode}
                inputType={inputTypeTpCreate}
                existingInput={inputToEdit}
            />
        </div>
    );
};
CensysInputs.propTypes = {
    title: PropTypes.string,
};
CensysInputs.defaultProps = {
    title: 'Censys Inputs',
};
export default CensysInputs;
