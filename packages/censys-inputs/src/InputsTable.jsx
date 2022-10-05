import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import CloneIcon from '@splunk/react-icons/Clone';
import PencilIcon from '@splunk/react-icons/Pencil';
import TrashIcon from '@splunk/react-icons/Trash';
import Button from '@splunk/react-ui/Button';
import DL from '@splunk/react-ui/DefinitionList';
import Switch from '@splunk/react-ui/Switch';
import Table from '@splunk/react-ui/Table';

import { inputs } from '@splunk/censys-utils';

const DEFAULT_HEADERS = [
    {
        label: 'Name',
        key: 'name',
        align: 'left',
        width: 200,
        minWidth: 185,
    },
    {
        label: 'Type',
        key: 'type',
        align: 'left',
        width: 175,
        minWidth: 175,
    },
    {
        label: 'Interval',
        key: 'interval',
        align: 'left',
        width: 100,
        minWidth: 85,
        units: 'sec',
    },
    {
        label: 'Index',
        key: 'index',
        align: 'left',
        width: 85,
        minWidth: 75,
    },
    {
        label: 'Authentication',
        key: 'authentication',
        align: 'left',
        width: 145,
        minWidth: 135,
    },
    {
        label: 'Status',
        key: 'disabled',
        align: 'left',
        width: 125,
        minWidth: 125,
    },
    {
        label: 'Actions',
        key: 'actions',
        align: 'left',
        width: 150,
        minWidth: 150,
    },
];

const InputsTable = ({ inputsData, onEdit, onClone, onDelete, onToggleStatus }) => {
    const [data, setData] = useState(inputsData);
    const [headers, setHeaders] = useState(DEFAULT_HEADERS);
    const [currentSortKey, setSortKey] = useState('name');
    const [sortDir, setSortDir] = useState('asc');

    useEffect(() => {
        setData(inputsData);
    }, [inputsData]);

    const handleSort = (e, { sortKey }) => {
        setSortKey(sortKey);
        setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    };

    const handleResizeColumn = (e, { columnId, index, width }) => {
        const newHeaders = [...headers];
        const selectedHeader = newHeaders.find((header) => header.key === columnId);
        if (selectedHeader) {
            newHeaders[index].width = Math.max(selectedHeader.minWidth, width);
            setHeaders(newHeaders);
        }
    };

    const handleToggle = (e, { name }) => {
        const newData = [...data];
        const selectedRow = newData.find((row) => row.name === name);
        if (selectedRow) {
            selectedRow.selected = !selectedRow.selected;
            setData(newData);
        }
    };

    const rowSelectionState = (tableData) => {
        const selectedRows = tableData.filter((row) => row.selected);
        const selectedRowCount = selectedRows.length;

        if (selectedRowCount === 0) {
            return 'none';
        }
        if (selectedRowCount === tableData.length) {
            return 'all';
        }
        return 'some';
    };

    const handleToggleAll = () => {
        const newData = JSON.parse(JSON.stringify(data));
        const selected = rowSelectionState(newData) !== 'all';
        newData.forEach((row) => {
            // eslint-disable-next-line no-param-reassign
            row.selected = selected;
        });
        setData(newData);
    };

    const getExpansionRow = (row) => {
        return (
            <Table.Row key={`${row.name}-expansion`}>
                <Table.Cell style={{ borderTop: 'none' }} colSpan={headers.length}>
                    <DL>
                        {/* TODO: Remove duplicates */}
                        <DL.Term>Name</DL.Term>
                        <DL.Description>{row.name}</DL.Description>
                        <DL.Term>Type</DL.Term>
                        <DL.Description>{row.type}</DL.Description>
                        <DL.Term>Interval</DL.Term>
                        <DL.Description>{row.interval.toString()}</DL.Description>
                        <DL.Term>Index</DL.Term>
                        <DL.Description>{row.index}</DL.Description>
                        <DL.Term>Authentication</DL.Term>
                        <DL.Description>{row.authentication}</DL.Description>
                        <DL.Term>Status</DL.Term>
                        <DL.Description>{row.disabled ? 'Disabled' : 'Enabled'}</DL.Description>
                        {/* TODO: Consider getting event count and auth status */}
                    </DL>
                </Table.Cell>
            </Table.Row>
        );
    };

    return (
        <Table
            stripeRows
            onRequestResizeColumn={handleResizeColumn}
            onRequestToggleAllRows={handleToggleAll}
            rowSelection={rowSelectionState(data)}
            headType="fixed"
            innerStyle={{ maxHeight: '80vh' }}
            rowExpansion="multi"
        >
            <Table.Head>
                {headers.map((header) => (
                    <Table.HeadCell
                        key={header.key}
                        columnId={header.key}
                        align={header.align}
                        width={header.width}
                        onSort={handleSort}
                        sortKey={header.key}
                        sortDir={header.key === currentSortKey ? sortDir : 'none'}
                    >
                        {header.label}
                    </Table.HeadCell>
                ))}
            </Table.Head>
            <Table.Body>
                {data
                    .sort((rowA, rowB) => {
                        if (sortDir === 'asc') {
                            return rowA[currentSortKey] > rowB[currentSortKey] ? 1 : -1;
                        }
                        if (sortDir === 'desc') {
                            return rowB[currentSortKey] > rowA[currentSortKey] ? 1 : -1;
                        }
                        return 0;
                    })
                    .map((row) => (
                        <Table.Row
                            key={row.name}
                            expansionRow={getExpansionRow(row)}
                            onRequestToggle={handleToggle}
                            // onClick={handleRowClick}
                            data={row}
                            selected={row.selected}
                        >
                            {headers.map((header) => {
                                if (header.key === 'disabled') {
                                    return (
                                        <Table.Cell key={`${row.name}-toggle`} align={header.align}>
                                            <Switch
                                                key={header.name}
                                                value={row.name}
                                                selected={!row.disabled}
                                                appearance="toggle"
                                                onClick={onToggleStatus}
                                            >
                                                {row.disabled ? 'Disabled' : 'Enabled'}
                                            </Switch>
                                        </Table.Cell>
                                    );
                                }
                                if (header.key === 'actions') {
                                    return (
                                        <Table.Cell
                                            key={`${row.name}-actions`}
                                            align={header.align}
                                        >
                                            <Button
                                                icon={<PencilIcon />}
                                                onClick={onEdit}
                                                value={row.name}
                                                action="edit"
                                            />
                                            <Button
                                                icon={<CloneIcon />}
                                                onClick={onClone}
                                                value={row.name}
                                                action="copy"
                                            />
                                            <Button
                                                icon={<TrashIcon />}
                                                onClick={onDelete}
                                                value={row.name}
                                                action="delete"
                                            />
                                        </Table.Cell>
                                    );
                                }
                                let cellValue = row[header.key].toString();
                                if (header?.units) {
                                    cellValue = `${cellValue} ${header.units}`;
                                }
                                if (header.key === 'type') {
                                    cellValue = inputs.inputTypeNames[cellValue];
                                }
                                return (
                                    <Table.Cell key={row[header.key]} align={header.align}>
                                        {cellValue}
                                    </Table.Cell>
                                );
                            })}
                        </Table.Row>
                    ))}
            </Table.Body>
        </Table>
    );
};
InputsTable.propTypes = {
    inputsData: PropTypes.arrayOf(PropTypes.shape({})),
    onEdit: PropTypes.func.isRequired,
    onClone: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
    onToggleStatus: PropTypes.func.isRequired,
};
InputsTable.defaultProps = {
    inputsData: [],
};
export default InputsTable;
