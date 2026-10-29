import React from 'react';
import {
  Box,
  Button,
  LinearProgress,
  LinearProgressProps,
  Typography,
  Divider,
  TextField,
  useTheme,
} from '@mui/material';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { ApiServerModelsRmfApiTaskStateStatus as TaskStatus, TaskState } from 'api-client';
import { base } from 'react-components';
import { TaskInspector } from './task-inspector';
import { RmfAppContext } from '../rmf-app';

const LinearProgressWithLabel = (props: LinearProgressProps & { value: number }) => {
  return (
    <Box component="div" sx={{ display: 'flex', alignItems: 'center' }}>
      <Box component="div" sx={{ width: '100%', mr: 1 }}>
        <LinearProgress variant="determinate" {...props} />
      </Box>
      <Box component="div" sx={{ minWidth: 35 }}>
        <Typography variant="body2" color="text.secondary">{`${Math.round(
          props.value,
        )}%`}</Typography>
      </Box>
    </Box>
  );
};

const setTaskDialogColor = (taskStatus?: TaskStatus | null) => {
  if (!taskStatus) {
    return base.palette.background.default;
  }

  switch (taskStatus) {
    case TaskStatus.Failed:
      return base.palette.error.dark;

    case TaskStatus.Underway:
      return base.palette.success.dark;

    case TaskStatus.Queued:
      return base.palette.info.main;

    default:
      return base.palette.background.default;
  }
};

export interface TaskSummaryProps {
  onClose: () => void;
  task: TaskState | null;
}

export const TaskSummary = React.memo((props: TaskSummaryProps) => {
  const rmf = React.useContext(RmfAppContext);

  const { onClose, task } = props;

  const [openTaskDetailsLogs, setOpenTaskDetailsLogs] = React.useState(false);
  const [taskState, setTaskState] = React.useState<TaskState | null>(null);
  const [isOpen, setIsOpen] = React.useState(true);

  const taskProgress = React.useMemo(() => {
    if (
      !taskState ||
      !taskState.estimate_millis ||
      !taskState.unix_millis_start_time ||
      !taskState.unix_millis_finish_time
    ) {
      console.log(`无法计算任务进度`);
      return undefined;
    }

    return Math.min(
      1.0 -
        taskState.estimate_millis /
          (taskState.unix_millis_finish_time - taskState.unix_millis_start_time),
      1,
    );
  }, [taskState]);

  React.useEffect(() => {
    if (!rmf || !task) {
      return;
    }
    const sub = rmf
      .getTaskStateObs(task.booking.id)
      .subscribe((subscribedTask) => setTaskState(subscribedTask));
    return () => sub.unsubscribe();
  }, [rmf, task]);

  const getTaskPhaseDetails = (task: TaskState) => {
    if (!task.phases || !task.active) {
      return '无法获取当前任务阶段';
    }

    const message = Object.values(task.phases)[task.active - 1]?.detail;

    if (message) {
      return message;
    }

    const categoryString = Object.values(task.phases)[task.active - 1]?.category
      ? ` 类别 ${Object.values(task.phases)[task.active - 1].category}`
      : '';

    return `无法获取当前任务阶段详情，编号 ${task.booking.id}${categoryString}`;
  };

  const returnDialogContent = () => {
    const contents = [
      {
        title: '编号',
        value: taskState ? taskState.booking.id : '任务状态无效。',
      },
      {
        title: '当前阶段',
        value: taskState ? getTaskPhaseDetails(taskState) : '任务状态无效。',
      },
    ];

    const theme = useTheme();

    return (
      <>
        {contents.map((message, index) => (
          <div key={index}>
            <TextField
              label={message.title}
              id="standard-size-small"
              size="small"
              variant="filled"
              sx={{
                background: theme.palette.background.default,
                '&:hover': {
                  backgroundColor: theme.palette.background.default,
                },
              }}
              fullWidth={true}
              multiline
              maxRows={4}
              margin="dense"
              value={message.value}
            />
          </div>
        ))}
      </>
    );
  };

  return (
    <Dialog
      PaperProps={{
        style: {
          backgroundColor: setTaskDialogColor(taskState?.status),
          boxShadow: 'none',
        },
      }}
      open={isOpen}
      onClose={() => {
        setIsOpen(false);
        onClose();
      }}
      fullWidth
      maxWidth="sm"
    >
      <DialogTitle align="center">任务概况</DialogTitle>
      <Divider />
      <DialogTitle align="center">任务状态</DialogTitle>
      {taskProgress && (
        <Box component="div" sx={{ width: '90%', ml: 3 }}>
          <LinearProgressWithLabel value={taskProgress * 100} />
        </Box>
      )}
      <DialogContent>{returnDialogContent()}</DialogContent>
      <DialogActions sx={{ justifyContent: 'center' }}>
        <Button
          size="small"
          variant="contained"
          onClick={() => setOpenTaskDetailsLogs(true)}
          autoFocus
        >
          查看详情
        </Button>
      </DialogActions>
      {openTaskDetailsLogs && (
        <TaskInspector task={taskState} onClose={() => setOpenTaskDetailsLogs(false)} />
      )}
    </Dialog>
  );
});
