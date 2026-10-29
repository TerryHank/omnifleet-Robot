import { zhCN } from '@mui/x-data-grid';
import { TortoiseContribPydanticCreatorApiServerModelsTortoiseModelsBeaconsBeaconStateLeaf as BeaconState } from 'api-client';
import { DataGrid, GridColDef, GridValueGetterParams, GridCellParams } from '@mui/x-data-grid';
import { Box, SxProps, Typography, useTheme } from '@mui/material';
import React from 'react';

export interface BeaconDataGridTableProps {
  beacons: BeaconState[];
}

export function BeaconDataGridTable({ beacons }: BeaconDataGridTableProps): JSX.Element {
  const theme = useTheme();

  const OpModeState = (params: GridCellParams): React.ReactNode => {
    const opModeStateLabelStyle: SxProps = (() => {
      const online = {
        color: theme.palette.success.main,
      };
      const offline = {
        color: theme.palette.error.main,
      };

      return params.row.online ? online : offline;
    })();

    return (
      <Box component="div" sx={opModeStateLabelStyle}>
        <Typography
          data-testid="op-mode-state"
          component="p"
          sx={{
            fontWeight: 'bold',
            fontSize: 14,
          }}
        >
          {params.row.online ? '在线' : '离线'}
        </Typography>
      </Box>
    );
  };

  const ActivatedState = (params: GridCellParams): React.ReactNode => {
    const activatedStateLabelStyle: SxProps = (() => {
      const on = {
        color: theme.palette.success.main,
      };
      const off = {
        color: theme.palette.error.main,
      };

      return params.row.activated ? on : off;
    })();

    return (
      <Box component="div" sx={activatedStateLabelStyle}>
        <Typography
          data-testid="activated-state"
          component="p"
          sx={{
            fontWeight: 'bold',
            fontSize: 14,
          }}
        >
          {params.row.activated ? '开启' : '关闭'}
        </Typography>
      </Box>
    );
  };

  const columns: GridColDef[] = [
    {
      field: 'beaconName',
      headerName: '名称',
      width: 90,
      valueGetter: (params: GridValueGetterParams) => params.row.id,
      flex: 1,
      filterable: true,
    },
    {
      field: 'opMode',
      headerName: '运行模式',
      width: 150,
      editable: false,
      flex: 1,
      renderCell: OpModeState,
      filterable: true,
    },
    {
      field: 'levelName',
      headerName: '楼层',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) => params.row.level ?? '暂无',
      flex: 1,
      filterable: true,
    },
    {
      field: 'beaconCategory',
      headerName: '类型',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) => params.row.category ?? '暂无',
      flex: 1,
      filterable: true,
    },
    {
      field: 'beaconState',
      headerName: '信号灯状态',
      width: 150,
      editable: false,
      flex: 1,
      renderCell: ActivatedState,
      filterable: true,
    },
  ];

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <DataGrid
        autoHeight={true}
        getRowId={(l) => l.id}
        rows={beacons}
        pageSize={5}
        rowHeight={38}
        columns={columns}
        rowsPerPageOptions={[5]}
        localeText={{
          ...zhCN.components.MuiDataGrid.defaultProps.localeText,
          noRowsLabel: '暂无信号灯。',
        }}
        disableVirtualization={true}
      />
    </div>
  );
}
