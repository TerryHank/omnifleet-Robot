import {
  DataGrid,
  GridColDef,
  GridEventListener,
  GridValueGetterParams,
  MuiEvent,
  GridRowParams,
  GridCellParams,
} from '@mui/x-data-grid';
import { Box, SxProps, Typography, useTheme } from '@mui/material';
import * as React from 'react';
import { ApiServerModelsRmfApiRobotStateStatus as RobotStatus } from 'api-client';
import { RobotTableData } from './robot-table';
import { robotStatusToUpperCase } from './utils';

export interface RobotDataGridTableProps {
  onRobotClick?(ev: MuiEvent<React.MouseEvent<HTMLElement>>, robotName: RobotTableData): void;
  robots: RobotTableData[];
}

export function RobotDataGridTable({ onRobotClick, robots }: RobotDataGridTableProps): JSX.Element {
  const handleEvent: GridEventListener<'rowClick'> = (
    params: GridRowParams,
    event: MuiEvent<React.MouseEvent<HTMLElement>>,
  ) => {
    if (onRobotClick) {
      onRobotClick(event, params.row);
    }
  };

  const Status = (params: GridCellParams): React.ReactNode => {
    const theme = useTheme();
    const statusLabelStyle: SxProps = (() => {
      const error = {
        color: theme.palette.error.main,
      };
      const charging = {
        color: theme.palette.info.main,
      };
      const working = {
        color: theme.palette.success.main,
      };
      const defaultColor = {
        color: theme.palette.warning.main,
      };

      switch (params.row.status) {
        case RobotStatus.Error:
          return error;
        case RobotStatus.Charging:
          return charging;
        case RobotStatus.Working:
          return working;
        default:
          return defaultColor;
      }
    })();

    return (
      <Box component="div" sx={statusLabelStyle}>
        <Typography
          data-testid="status"
          component="p"
          sx={{
            fontWeight: 'bold',
            fontSize: 14,
          }}
        >
          {robotStatusToUpperCase(params.row.status)}
        </Typography>
      </Box>
    );
  };

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: '名称',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) => params.row.name,
      flex: 1,
      filterable: true,
    },
    {
      field: 'fleet',
      headerName: '车队',
      width: 90,
      valueGetter: (params: GridValueGetterParams) => params.row.fleet,
      flex: 1,
      filterable: true,
    },
    {
      field: 'estFinishTime',
      headerName: '预计任务完成时间',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) =>
        params.row.estFinishTime ? new Date(params.row.estFinishTime).toLocaleString('zh-CN') : '-',
      flex: 1,
      filterable: true,
    },
    {
      field: 'level',
      headerName: '楼层',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) => params.row.level,
      flex: 1,
      filterable: true,
    },
    {
      field: 'battery',
      headerName: '电量',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) => `${params.row.battery * 100}%`,
      flex: 1,
      filterable: true,
    },
    {
      field: 'lastUpdateTime',
      headerName: '最近更新',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) =>
        params.row.lastUpdateTime ? new Date(params.row.lastUpdateTime).toLocaleString('zh-CN') : '-',
      flex: 1,
      filterable: true,
    },
    {
      field: 'status',
      headerName: '状态',
      editable: false,
      flex: 1,
      renderCell: Status,
      filterable: true,
    },
  ];

  return (
    <DataGrid
      autoHeight={true}
      getRowId={(r) => r.name}
      rows={robots}
      pageSize={5}
      rowHeight={38}
      columns={columns}
      rowsPerPageOptions={[5]}
      onRowClick={handleEvent}
      initialState={{
        sorting: {
          sortModel: [{ field: 'name', sort: 'asc' }],
        },
      }}
      disableVirtualization={true}
    />
  );
}
