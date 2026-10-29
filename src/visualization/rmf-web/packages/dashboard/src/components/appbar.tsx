import {
  AccountCircle,
  AddOutlined,
  Help,
  Notifications,
  Report,
  Settings,
  Warning as Issue,
} from '@mui/icons-material';
import {
  Badge,
  Button,
  CardContent,
  Divider,
  FormControl,
  FormControlLabel,
  FormLabel,
  IconButton,
  Menu,
  MenuItem,
  Radio,
  RadioGroup,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  TortoiseContribPydanticCreatorApiServerModelsTortoiseModelsAlertsAlertLeaf as Alert,
  TaskFavoritePydantic as TaskFavorite,
  TaskRequest,
} from 'api-client';
import React from 'react';
import {
  displayText,
  AppBarTab,
  CreateTaskForm,
  CreateTaskFormProps,
  HeaderBar,
  LogoButton,
  NavigationBar,
} from 'react-components';
import { useNavigate, useLocation } from 'react-router-dom';
import { UserProfileContext } from 'rmf-auth';
import { ThemeMode } from '../settings';
import {
  AdminRoute,
  CustomRoute1,
  CustomRoute2,
  DashboardRoute,
  RobotsRoute,
  TasksRoute,
} from '../util/url';
import {
  AppConfigContext,
  AppControllerContext,
  ResourcesContext,
  SettingsContext,
} from './app-contexts';
import { AppEvents } from './app-events';
import { RmfAppContext } from './rmf-app';
import { parseTasksFile } from './tasks/utils';
import { Subscription } from 'rxjs';
import { formatDistance } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { useCreateTaskFormData } from '../hooks/useCreateTaskForm';
import { toApiSchedule } from './tasks/utils';
import useGetUsername from '../hooks/useFetchUser';

export type TabValue = 'infrastructure' | 'robots' | 'tasks' | 'custom1' | 'custom2' | 'admin';

const locationToTabValue = (pathname: string): TabValue | undefined => {
  const routes: { prefix: string; tabValue: TabValue }[] = [
    { prefix: RobotsRoute, tabValue: 'robots' },
    { prefix: TasksRoute, tabValue: 'tasks' },
    { prefix: CustomRoute1, tabValue: 'custom1' },
    { prefix: CustomRoute2, tabValue: 'custom2' },
    { prefix: AdminRoute.replace(/\*/g, ''), tabValue: 'admin' },
    { prefix: DashboardRoute, tabValue: 'infrastructure' },
  ];

  // `DashboardRoute` being the root, it is a prefix to all routes, so we need to check exactly.
  const matchingRoute = routes.find((route) => pathname.startsWith(route.prefix));
  return matchingRoute?.tabValue;
};

function AppSettings() {
  const settings = React.useContext(SettingsContext);
  const appController = React.useContext(AppControllerContext);
  return (
    <FormControl>
      <FormLabel id="theme-label">主题</FormLabel>
      <RadioGroup row aria-labelledby="theme-label">
        <FormControlLabel
          value={ThemeMode.Default}
          control={<Radio />}
          label="默认"
          checked={settings.themeMode === ThemeMode.Default}
          onChange={() =>
            appController.updateSettings({ ...settings, themeMode: ThemeMode.Default })
          }
        />
        <FormControlLabel
          value={ThemeMode.RmfLight}
          control={<Radio />}
          label="RMF 浅色"
          checked={settings.themeMode === ThemeMode.RmfLight}
          onChange={() =>
            appController.updateSettings({ ...settings, themeMode: ThemeMode.RmfLight })
          }
        />
        <FormControlLabel
          value={ThemeMode.RmfDark}
          control={<Radio />}
          label="RMF 深色"
          checked={settings.themeMode === ThemeMode.RmfDark}
          onChange={() =>
            appController.updateSettings({ ...settings, themeMode: ThemeMode.RmfDark })
          }
        />
      </RadioGroup>
    </FormControl>
  );
}

export interface AppBarProps {
  extraToolbarItems?: React.ReactNode;

  // TODO: change the alarm status to required when we have an alarm
  // service working properly in the backend
  alarmState?: boolean | null;
}

export const AppBar = React.memo(({ extraToolbarItems }: AppBarProps): React.ReactElement => {
  const rmf = React.useContext(RmfAppContext);
  const resourceManager = React.useContext(ResourcesContext);
  const { showAlert } = React.useContext(AppControllerContext);
  const navigate = useNavigate();
  const location = useLocation();
  const tabValue = React.useMemo(() => locationToTabValue(location.pathname), [location]);
  const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null);
  const { authenticator } = React.useContext(AppConfigContext);
  const profile = React.useContext(UserProfileContext);
  const [settingsAnchor, setSettingsAnchor] = React.useState<HTMLElement | null>(null);
  const [openCreateTaskForm, setOpenCreateTaskForm] = React.useState(false);
  const [favoritesTasks, setFavoritesTasks] = React.useState<TaskFavorite[]>([]);
  const [refreshTaskAppCount, setRefreshTaskAppCount] = React.useState(0);
  const [alertListAnchor, setAlertListAnchor] = React.useState<HTMLElement | null>(null);
  const [unacknowledgedAlertsNum, setUnacknowledgedAlertsNum] = React.useState(0);
  const [unacknowledgedAlertList, setUnacknowledgedAlertList] = React.useState<Alert[]>([]);

  const { waypointNames, pickupPoints, dropoffPoints, cleaningZoneNames } =
    useCreateTaskFormData(rmf);
  const username = useGetUsername(rmf);

  async function handleLogout(): Promise<void> {
    try {
      await authenticator.logout();
    } catch (e) {
      console.error(`error logging out: ${(e as Error).message}`);
    }
  }

  React.useEffect(() => {
    const sub = AppEvents.refreshTaskApp.subscribe({
      next: () => setRefreshTaskAppCount((oldValue) => ++oldValue),
    });
    return () => sub.unsubscribe();
  }, []);



  React.useEffect(() => {
    if (!rmf) {
      return;
    }

    const subs: Subscription[] = [];
    subs.push(
      AppEvents.refreshAlert.subscribe({
        next: () => {
          (async () => {
            const resp = await rmf.alertsApi.getAlertsAlertsGet();
            const alerts = resp.data as Alert[];
            setUnacknowledgedAlertsNum(
              alerts.filter(
                (alert) => !(alert.acknowledged_by && alert.unix_millis_acknowledged_time),
              ).length,
            );
          })();
        },
      }),
    );

    // Get the initial number of unacknowledged alerts
    (async () => {
      const resp = await rmf.alertsApi.getAlertsAlertsGet();
      const alerts = resp.data as Alert[];
      setUnacknowledgedAlertsNum(
        alerts.filter((alert) => !(alert.acknowledged_by && alert.unix_millis_acknowledged_time))
          .length,
      );
    })();
    return () => subs.forEach((s) => s.unsubscribe());
  }, [rmf]);

  const submitTasks = React.useCallback<Required<CreateTaskFormProps>['submitTasks']>(
    async (taskRequests, schedule) => {
      if (!rmf) {
        throw new Error('任务接口不可用');
      }
      if (!schedule) {
        await Promise.all(
          taskRequests.map((request) =>
            rmf.tasksApi.postDispatchTaskTasksDispatchTaskPost({
              type: 'dispatch_task_request',
              request,
            }),
          ),
        );
      } else {
        const scheduleRequests = taskRequests.map((req) => toApiSchedule(req, schedule));
        await Promise.all(
          scheduleRequests.map((req) => rmf.tasksApi.postScheduledTaskScheduledTasksPost(req)),
        );
      }
      AppEvents.refreshTaskApp.next();
    },
    [rmf],
  );

  const uploadFileInputRef = React.useRef<HTMLInputElement>(null);
  const tasksFromFile = (): Promise<TaskRequest[]> => {
    return new Promise((res) => {
      const fileInputEl = uploadFileInputRef.current;
      if (!fileInputEl) {
        return [];
      }
      let taskFiles: TaskRequest[];
      const listener = async () => {
        try {
          if (!fileInputEl.files || fileInputEl.files.length === 0) {
            return res([]);
          }
          try {
            taskFiles = parseTasksFile(await fileInputEl.files[0].text());
          } catch (err) {
            showAlert('error', (err as Error).message, 5000);
            return res([]);
          }
          // only submit tasks when all tasks are error free
          return res(taskFiles);
        } finally {
          fileInputEl.removeEventListener('input', listener);
          fileInputEl.value = '';
        }
      };
      fileInputEl.addEventListener('input', listener);
      fileInputEl.click();
    });
  };

  //#region 'Favorite Task'
  React.useEffect(() => {
    if (!rmf) {
      return;
    }
    (async () => {
      const resp = await rmf.tasksApi.getFavoritesTasksFavoriteTasksGet();

      const results = resp.data as TaskFavorite[];
      setFavoritesTasks(results);
    })();

    return () => {
      setFavoritesTasks([]);
    };
  }, [rmf, refreshTaskAppCount]);

  const submitFavoriteTask = React.useCallback<Required<CreateTaskFormProps>['submitFavoriteTask']>(
    async (taskFavoriteRequest) => {
      if (!rmf) {
        throw new Error('任务接口不可用');
      }
      await rmf.tasksApi.postFavoriteTaskFavoriteTasksPost(taskFavoriteRequest);
      AppEvents.refreshTaskApp.next();
    },
    [rmf],
  );

  const deleteFavoriteTask = React.useCallback<Required<CreateTaskFormProps>['deleteFavoriteTask']>(
    async (favoriteTask) => {
      if (!rmf) {
        throw new Error('任务接口不可用');
      }
      if (!favoriteTask.id) {
        throw new Error('必须提供编号');
      }

      await rmf.tasksApi.deleteFavoriteTaskFavoriteTasksFavoriteTaskIdDelete(favoriteTask.id);
      AppEvents.refreshTaskApp.next();
    },
    [rmf],
  );
  //#endregion 'Favorite Task'

  const handleOpenAlertList = (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
    if (!rmf) {
      return;
    }
    (async () => {
      const { data: alerts } = await rmf.alertsApi.getAlertsAlertsGet();
      const unackList = alerts.filter(
        (alert) => !alert.acknowledged_by && !alert.unix_millis_acknowledged_time,
      );
      setUnacknowledgedAlertList(unackList.reverse());
    })();
    setAlertListAnchor(event.currentTarget);
  };

  const openAlertDialog = (alert: Alert) => {
    AppEvents.alertListOpenedAlert.next(alert);
  };

  const timeDistance = (time: number) => {
    return formatDistance(new Date(), new Date(time), { locale: zhCN });
  };

  return (
    <>
      <HeaderBar>
        <LogoButton src="/omnifleet-logo.jpg" alt="OmniFleet 标志" sx={{ width: 52, height: 52, mx: 1 }} /><Typography variant="h6" sx={{ whiteSpace: 'nowrap', mr: 2 }}>任务调度系统</Typography>
        <NavigationBar value={tabValue}>
          <AppBarTab
            label="地图"
            value="infrastructure"
            aria-label="地图"
            onTabClick={() => navigate(DashboardRoute)}
          />
          <AppBarTab
            label="系统概览"
            value="robots"
            aria-label="系统概览"
            onTabClick={() => navigate(RobotsRoute)}
          />
          <AppBarTab
            label="任务"
            value="tasks"
            aria-label="任务"
            onTabClick={() => navigate(TasksRoute)}
          />
          <AppBarTab
            label="自定义页面 1"
            value="custom1"
            aria-label="自定义页面 1"
            onTabClick={() => navigate(CustomRoute1)}
          />
          <AppBarTab
            label="自定义页面 2"
            value="custom2"
            aria-label="自定义页面 2"
            onTabClick={() => navigate(CustomRoute2)}
          />
          {profile?.user.is_admin && (
            <AppBarTab
              label="管理"
              value="admin"
              aria-label="管理"
              onTabClick={() => navigate(AdminRoute)}
            />
          )}
        </NavigationBar>
        <Toolbar variant="dense" sx={{ textAlign: 'right', flexGrow: -1 }}>
          <Button
            id="create-new-task-button"
            aria-label="新建任务"
            sx={{ whiteSpace: 'nowrap', flexShrink: 0 }}
            color="secondary"
            variant="contained"
            size="small"
            onClick={() => location.pathname.startsWith('/rmf/') ? setOpenCreateTaskForm(true) : navigate(TasksRoute)}
          >
            <AddOutlined />
            新建任务
          </Button>
          <Tooltip title="通知">
            <IconButton
              id="alert-list-button"
              aria-label="告警列表"
              color="inherit"
              onClick={handleOpenAlertList}
            >
              <Badge badgeContent={unacknowledgedAlertsNum} color="secondary">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={alertListAnchor}
            open={!!alertListAnchor}
            onClose={() => setAlertListAnchor(null)}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            PaperProps={{
              style: {
                maxHeight: '20rem',
                maxWidth: '30rem',
              },
            }}
          >
            {unacknowledgedAlertList.length === 0 ? (
              <MenuItem dense disabled>
                <Typography variant="body2" noWrap>
                  暂无待确认的告警
                </Typography>
              </MenuItem>
            ) : (
              unacknowledgedAlertList.map((alert) => (
                <Tooltip
                  key={alert.id}
                  title={
                    <React.Fragment>
                      <Typography>告警</Typography>
                      <Typography>编号： {alert.original_id}</Typography>
                      <Typography>类型： {displayText(alert.category)}</Typography>
                      <Typography>
                        创建时间： {new Date(alert.unix_millis_created_time).toLocaleString('zh-CN')}
                      </Typography>
                    </React.Fragment>
                  }
                  placement="right"
                >
                  <MenuItem
                    dense
                    onClick={() => {
                      openAlertDialog(alert);
                      setAlertListAnchor(null);
                    }}
                    divider
                  >
                    <Report />
                    <Typography variant="body2" mx={1} noWrap>
                      任务 {alert.original_id} 发生告警于{' '}
                      {timeDistance(alert.unix_millis_created_time)} 前
                    </Typography>
                  </MenuItem>
                </Tooltip>
              ))
            )}
          </Menu>
          <Divider orientation="vertical" sx={{ marginLeft: 1, marginRight: 2 }} />
          <Typography variant="caption" noWrap sx={{ flexShrink: 0 }}>基于 Open-RMF</Typography>
          {extraToolbarItems}
          <Tooltip title="设置">
            <IconButton
              id="show-settings-btn"
              aria-label="设置"
              color="inherit"
              onClick={(ev) => setSettingsAnchor(ev.currentTarget)}
            >
              <Settings />
            </IconButton>
          </Tooltip>
          <Tooltip title="帮助">
            <IconButton
              id="show-help-btn"
              aria-label="帮助"
              color="inherit"
              onClick={() => window.open(resourceManager?.helpLink, '_blank')}
            >
              <Help />
            </IconButton>
          </Tooltip>
          <Tooltip title="反馈问题">
            <IconButton
              id="show-warning-btn"
              aria-label="警告"
              color="inherit"
              onClick={() => window.open(resourceManager?.reportIssue, '_blank')}
            >
              <Issue />
            </IconButton>
          </Tooltip>
          {profile && (
            <>
              <Tooltip title="个人资料">
                <IconButton
                  id="user-btn"
                  aria-label={"账户"}
                  color="inherit"
                  onClick={(event) => setAnchorEl(event.currentTarget)}
                >
                  <AccountCircle />
                </IconButton>
              </Tooltip>
              <Menu
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={!!anchorEl}
                onClose={() => setAnchorEl(null)}
              >
                <MenuItem id="logout-btn" onClick={handleLogout}>
                  退出登录
                </MenuItem>
              </Menu>
            </>
          )}
        </Toolbar>
      </HeaderBar>
      <Menu
        anchorEl={settingsAnchor}
        open={!!settingsAnchor}
        onClose={() => setSettingsAnchor(null)}
      >
        <CardContent>
          <AppSettings />
        </CardContent>
      </Menu>
      {openCreateTaskForm && (
        <CreateTaskForm
          user={username ? username : '未知用户'}
          patrolWaypoints={waypointNames}
          cleaningZones={cleaningZoneNames}
          pickupPoints={pickupPoints}
          dropoffPoints={dropoffPoints}
          favoritesTasks={favoritesTasks}
          open={openCreateTaskForm}
          onClose={() => setOpenCreateTaskForm(false)}
          submitTasks={submitTasks}
          submitFavoriteTask={submitFavoriteTask}
          deleteFavoriteTask={deleteFavoriteTask}
          tasksFromFile={tasksFromFile}
          onSuccess={() => {
            setOpenCreateTaskForm(false);
            showAlert('success', '已创建任务');
          }}
          onFail={(e) => {
            showAlert('error', `创建任务失败： ${e.message}`);
          }}
          onSuccessFavoriteTask={(message) => {
            showAlert('success', message);
          }}
          onFailFavoriteTask={(e) => {
            showAlert('error', `创建或删除收藏任务失败： ${e.message}`);
          }}
          onSuccessScheduling={() => {
            setOpenCreateTaskForm(false);
            showAlert('success', '已创建计划');
          }}
          onFailScheduling={(e) => {
            showAlert('error', `提交计划失败： ${e.message}`);
          }}
        />
      )}
    </>
  );
});

export default AppBar;
