import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { Controller, useForm } from 'react-hook-form';

import Button from '@splunk/react-ui/Button';
import ComboBox from '@splunk/react-ui/ComboBox';
import ControlGroup from '@splunk/react-ui/ControlGroup';
import Modal from '@splunk/react-ui/Modal';
import Number from '@splunk/react-ui/Number';
import Text from '@splunk/react-ui/Text';

import { defaultApp, inputs } from '@splunk/censys-utils';

export const DEFAULT_VALUES = {
    name: '',
    interval: 3600,
    index: 'main',
    authentication: 'Global',
};

export const InputModalMode = {
    create: 'create',
    edit: 'edit',
    clone: 'clone',
    delete: 'delete',
};

const InputModal = ({ isOpen, onClose, mode, inputType, existingInput }) => {
    const [title, setTitle] = useState('');
    const [indexes, setIndexes] = useState([]);
    const { control, handleSubmit, setValue, clearErrors, reset } = useForm({
        defaultValues: DEFAULT_VALUES,
    });

    useEffect(() => {
        const controller = new AbortController();
        inputs
            .getIndexes(-1, defaultApp, controller.signal)
            .then((newIndexes) => setIndexes(newIndexes));
        return () => controller?.abort();
    }, []);

    useEffect(() => {
        console.log('mode', mode);
        const titlePrefix = mode.charAt(0).toUpperCase() + mode.slice(1);
        if (inputType) {
            const inputTypeName = inputs.inputTypeNames[inputType];
            setTitle(`${titlePrefix} ${inputTypeName} Input`);
        } else {
            setTitle(`${titlePrefix} Input`);
        }
    }, [inputType, mode]);

    useEffect(() => {
        // TODO: Is there a better way to do this?
        // I tried using the defaultValues prop for useForm, but it didn't update correctly.
        if (existingInput) {
            if (existingInput?.name) {
                setValue('name', existingInput.name);
            }
            if (existingInput?.interval) {
                setValue('interval', parseInt(existingInput.interval, 10));
            }
            if (existingInput?.index) {
                setValue('index', existingInput.index);
            }
            if (existingInput?.authentication) {
                setValue('authentication', existingInput.authentication);
            }
        } else {
            reset(DEFAULT_VALUES);
            // setValue('name', '');
            // setValue('interval', 3600);
            // setValue('index', 'main');
            // setValue('authentication', 'Global');
        }
        clearErrors();
    }, [existingInput, setValue, clearErrors, reset]);

    const generateIndexOptions = () => {
        return indexes
            .filter((index) => index[0] !== '_')
            .map((index) => <ComboBox.Option key={`${index}-index`} value={index} />);
    };

    const onSubmit = (data) => {
        if (mode === InputModalMode.create || mode === InputModalMode.clone) {
            inputs.createInput(data.name, inputType, data.index, data.interval.toString());
        }
        if (mode === InputModalMode.edit) {
            const indexUpdated = data.index !== existingInput.index;
            const intervalUpdated = data.interval.toString() !== existingInput.interval;
            if (indexUpdated || intervalUpdated) {
                inputs.updateInput(
                    data.name,
                    inputType,
                    indexUpdated ? data.index : null,
                    intervalUpdated ? data.interval : null
                );
            }
        }
        if (mode === InputModalMode.delete) {
            inputs.deleteInput(data.name, inputType);
        }
        onClose();
    };

    return (
        <Modal onRequestClose={onClose} open={isOpen}>
            <Modal.Header title={title} onRequestClose={onClose} />
            <Modal.Body>
                <Controller
                    name="name"
                    control={control}
                    rules={{ required: true }}
                    render={({ field, fieldState }) => {
                        const hasError = fieldState?.error;
                        const creationHelp =
                            mode === 'create'
                                ? ' After creating an input, you cannot change its name.'
                                : '';
                        return (
                            <ControlGroup
                                label="Name"
                                help={`The name of the input.${creationHelp}`}
                                error={hasError}
                            >
                                <Text
                                    {...field}
                                    disabled={
                                        mode === InputModalMode.edit ||
                                        mode === InputModalMode.delete
                                    }
                                    error={hasError}
                                />
                            </ControlGroup>
                        );
                    }}
                />
                {mode !== InputModalMode.delete && (
                    <>
                        <Controller
                            name="interval"
                            control={control}
                            rules={{ required: true }}
                            render={({ field, fieldState }) => {
                                const hasError = fieldState.error !== undefined;
                                const onChange = (e, { value }) => {
                                    setValue(field.name, value);
                                };
                                return (
                                    <ControlGroup
                                        label="Interval"
                                        help="The interval in seconds at which the input will be run."
                                        error={hasError}
                                    >
                                        <Number {...field} onChange={onChange} error={hasError} />
                                    </ControlGroup>
                                );
                            }}
                        />
                        <Controller
                            name="index"
                            control={control}
                            rules={{ required: true }}
                            render={({ field, fieldState }) => {
                                const hasError = fieldState.error !== undefined;
                                const onChange = (e, { value }) => {
                                    setValue(field.name, value);
                                };
                                return (
                                    <ControlGroup
                                        label="Index"
                                        help="The index to which the input will write to."
                                        error={hasError}
                                    >
                                        <ComboBox {...field} onChange={onChange} error={hasError}>
                                            {generateIndexOptions()}
                                        </ComboBox>
                                    </ControlGroup>
                                );
                            }}
                        />
                        <Controller
                            name="authentication"
                            control={control}
                            rules={{ required: true }}
                            render={({ field, fieldState }) => {
                                const hasError = fieldState?.error;
                                return (
                                    <ControlGroup
                                        label="Authentication"
                                        help="Authentication type for the input."
                                        error={hasError}
                                    >
                                        <ComboBox {...field} error={hasError} />
                                    </ControlGroup>
                                );
                            }}
                        />
                    </>
                )}
            </Modal.Body>
            <Modal.Footer>
                <Button appearance="secondary" onClick={onClose} label="Cancel" />
                {mode === InputModalMode.delete ? (
                    <Button error label="Delete" onClick={handleSubmit(onSubmit)} />
                ) : (
                    <Button appearance="primary" label="Submit" onClick={handleSubmit(onSubmit)} />
                )}
            </Modal.Footer>
        </Modal>
    );
};
InputModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    mode: PropTypes.oneOf(Object.values(InputModalMode)).isRequired,
    inputType: PropTypes.oneOf([inputs.ASM_RISKS_INPUT_TYPE, inputs.ASM_LOGBOOK_INPUT_TYPE])
        .isRequired,
    existingInput: PropTypes.shape({
        type: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        interval: PropTypes.number.isRequired,
        index: PropTypes.string.isRequired,
        disabled: PropTypes.bool.isRequired,
        authentication: PropTypes.string.isRequired,
    }),
};
InputModal.defaultProps = {
    existingInput: null,
};
export default InputModal;
