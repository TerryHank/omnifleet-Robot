import { displayText } from '../display-text';
import {
  DataGrid,
  getGridDateOperators,
  getGridStringOperators,
  GridColDef,
  GridEventListener,
  GridValueGetterParams,
  MuiEvent,
  GridRowParams,
  GridCellParams,
  GridFilterModel,
  GridSortModel,
} from '@mui/x-data-grid';
import { styled, TextField, Stack, Typography, Tooltip } from '@mui/material';
import * as React from 'react';
import { TaskState, ApiServerModelsRmfApiTaskStateStatus as TaskStatus } from 'api-client';
import { InsertInvitation as ScheduleIcon, Person as UserIcon } from '@mui/icons-material/';

const classes = {
  taskActiveCell: 'MuiDataGrid-cell-active-cell',
  taskCancelledCell: 'MuiDataGrid-cell-cancelled-cell',
  taskCompletedCell: 'MuiDataGrid-cell-completed-cell',
  taskFailedCell: 'MuiDataGrid-cell-failed-cell',
  taskPendingCell: 'MuiDataGrid-cell-pending-cell',
  taskQueuedCell: 'MuiDataGrid-cell-queued-cell',
  taskUnknownCell: 'MuiDataGrid-cell-unknown-cell',
};

const StyledDataGrid = styled(DataGrid)(({ theme }) => ({
  [`& .${classes.taskActiveCell}`]: {
    backgroundColor: theme.palette.success.light,
    color: theme.palette.getContrastText(theme.palette.success.light),
  },
  [`& .${classes.taskCancelledCell}`]: {
    backgroundColor: theme.palette.grey[500],
    color: theme.palette.getContrastText(theme.palette.grey[500]),
  },
  [`& .${classes.taskCompletedCell}`]: {
    backgroundColor: theme.palette.info.light,
    color: theme.palette.getContrastText(theme.palette.info.light),
  },
  [`& .${classes.taskFailedCell}`]: {
    backgroundColor: theme.palette.error.main,
    color: theme.palette.getContrastText(theme.palette.error.main),
  },
  [`& .${classes.taskQueuedCell}`]: {
    backgroundColor: theme.palette.grey[300],
    color: theme.palette.getContrastText(theme.palette.grey[300]),
  },
  [`& .${classes.taskUnknownCell}`]: {
    backgroundColor: theme.palette.warning.main,
    color: theme.palette.getContrastText(theme.palette.warning.main),
  },
}));

export interface Tasks {
  isLoading: boolean;
  data: TaskState[];
  total: number;
  page: number;
  pageSize: number;
}

export interface FilterFields {
  model: GridFilterModel | undefined;
}

export interface SortFields {
  model: GridSortModel | undefined;
}

export type MuiMouseEvent = MuiEvent<React.MouseEvent<HTMLElement>>;

export interface TableDataGridState {
  tasks: Tasks;
  onTaskClick?(ev: MuiMouseEvent, task: TaskState): void;
  onPageChange: (newPage: number) => void;
  onPageSizeChange: (newPageSize: number) => void;
  setFilterFields: React.Dispatch<React.SetStateAction<FilterFields>>;
  setSortFields: React.Dispatch<React.SetStateAction<SortFields>>;
}

const TaskRequester = (requester: string | null): JSX.Element => {
  if (!requester) {
    return <Typography variant="body1">未知</Typography>;
  }

  /** When a task is created as scheduled,
   we save the requester as USERNAME__scheduled.
   Therefore, we remove the __schedule because the different icon is enough indicator to know
   if the task was adhoc or scheduled.
  */
  return (
    <Stack direction="row" alignItems="center" gap={1}>
      {requester.includes('scheduled') ? (
        <>
          <Tooltip title="用户计划">
            <ScheduleIcon />
          </Tooltip>
          <Typography variant="body1">{requester.split('__')[0]}</Typography>
        </>
      ) : (
        <>
          <Tooltip title="用户提交">
            <UserIcon />
          </Tooltip>
          <Typography variant="body1">{requester}</Typography>
        </>
      )}
    </Stack>
  );
};

export function TaskDataGridTable({
  tasks,
  onTaskClick,
  onPageChange,
  onPageSizeChange,
  setFilterFields,
  setSortFields,
}: TableDataGridState): JSX.Element {
  const handleEvent: GridEventListener<'rowClick'> = (
    params: GridRowParams,
    event: MuiMouseEvent,
  ) => {
    if (onTaskClick) {
      onTaskClick(event, params.row);
    }
  };

  const getMinimalStringFilterOperators = getGridStringOperators().filter(
    // TODO: implement contains on the server end as well
    (operator) => operator.value === 'equals',
  );

  const getMinimalDateOperators = getGridDateOperators(true).filter(
    (operator) => operator.value === 'onOrAfter' || operator.value === 'onOrBefore',
  );

  const columns: GridColDef[] = [
    {
      field: 'unix_millis_request_time',
      headerName: '日期',
      width: 150,
      editable: false,
      renderCell: (cellValues) => {
        return (
          <TextField
            variant="standard"
            value={
              cellValues.row.booking.unix_millis_request_time
                ? `${new Date(
                    cellValues.row.booking.unix_millis_request_time,
                  ).toLocaleDateString('zh-CN')}`
                : '未知'
            }
            InputProps={{ disableUnderline: true }}
            multiline
          />
        );
      },
      flex: 1,
      filterOperators: getMinimalDateOperators,
      filterable: true,
    },
    {
      field: 'requester',
      headerName: '请求者',
      minWidth: 160,
      editable: false,
      renderCell: (cellValues) => TaskRequester(cellValues.row.booking.requester),
      flex: 2,
      filterOperators: getMinimalStringFilterOperators,
      filterable: true,
    },
    {
      field: 'id_',
      headerName: '编号',
      width: 90,
      valueGetter: (params: GridValueGetterParams) => params.row.booking.id,
      flex: 1,
      filterOperators: getMinimalStringFilterOperators,
      filterable: true,
    },
    {
      field: 'category',
      valueFormatter: (params) => displayText(params.value),
      headerName: '类别',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) =>
        params.row.category ? params.row.category : '未知',
      flex: 1,
      filterOperators: getMinimalStringFilterOperators,
      filterable: true,
    },
    {
      field: 'assigned_to',
      headerName: '执行者',
      width: 150,
      editable: false,
      valueGetter: (params: GridValueGetterParams) =>
        params.row.assigned_to ? params.row.assigned_to.name : '未知',
      flex: 1,
      filterOperators: getMinimalStringFilterOperators,
      filterable: true,
    },
    {
      field: 'unix_millis_start_time',
      headerName: '开始时间',
      width: 150,
      editable: false,
      renderCell: (cellValues) => {
        return (
          <TextField
            variant="standard"
            value={
              cellValues.row.unix_millis_start_time
                ? `${new Date(
                    cellValues.row.unix_millis_start_time,
                  ).toLocaleDateString('zh-CN')} ${new Date(
                    cellValues.row.unix_millis_start_time,
                  ).toLocaleTimeString('zh-CN')}`
                : '未知'
            }
            InputProps={{ disableUnderline: true }}
            multiline
          />
        );
      },
      flex: 1,
      filterOperators: getMinimalDateOperators,
      filterable: true,
    },
    {
      field: 'unix_millis_finish_time',
      headerName: '结束时间',
      width: 150,
      editable: false,
      renderCell: (cellValues) => {
        return (
          <TextField
            variant="standard"
            value={
              cellValues.row.unix_millis_finish_time
                ? `${new Date(
                    cellValues.row.unix_millis_finish_time,
                  ).toLocaleDateString('zh-CN')} ${new Date(
                    cellValues.row.unix_millis_finish_time,
                  ).toLocaleTimeString('zh-CN')}`
                : '未知'
            }
            InputProps={{ disableUnderline: true }}
            multiline
          />
        );
      },
      flex: 1,
      filterOperators: getMinimalDateOperators,
      filterable: true,
    },
    {
      field: 'status',
      valueFormatter: (params) => displayText(params.value),
      headerName: '状态',
      editable: false,
      valueGetter: (params: GridValueGetterParams) =>
        params.row.status ? params.row.status : '未知',
      flex: 1,
      filterOperators: getMinimalStringFilterOperators,
      filterable: true,
    },
  ];

  const handleFilterModelChange = React.useCallback(
    (filterModel: GridFilterModel) => {
      setFilterFields({ model: filterModel });
    },
    [setFilterFields],
  );

  const handleSortModelChange = React.useCallback(
    (sortModel: GridSortModel) => {
      setSortFields({ model: sortModel });
    },
    [setSortFields],
  );

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <StyledDataGrid
        autoHeight
        getRowId={(r) => r.booking.id}
        rows={tasks.data}
        rowCount={tasks.total}
        loading={tasks.isLoading}
        pageSize={tasks.pageSize}
        rowsPerPageOptions={[10]}
        pagination
        paginationMode="server"
        filterMode="server"
        onFilterModelChange={handleFilterModelChange}
        sortingMode="server"
        onSortModelChange={handleSortModelChange}
        page={tasks.page - 1}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
        columns={columns}
        onRowClick={handleEvent}
        getCellClassName={(params: GridCellParams<string>) => {
          if (params.field === 'status') {
            switch (params.value) {
              case TaskStatus.Underway:
                return classes.taskActiveCell;
              case TaskStatus.Completed:
                return classes.taskCompletedCell;
              case TaskStatus.Canceled:
                return classes.taskCancelledCell;
              case TaskStatus.Failed:
                return classes.taskFailedCell;
              case TaskStatus.Queued:
                return classes.taskQueuedCell;
              default:
                return classes.taskUnknownCell;
            }
          }
          return '';
        }}
        disableVirtualization={true}
      />
    </div>
  );
}
