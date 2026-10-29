import {
  Alert,
  AlertProps,
  createTheme,
  CssBaseline,
  GlobalStyles,
  Grid,
  Snackbar,
} from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import { zhCN } from '@mui/material/locale';
import React from 'react';
import { rmfDark, rmfDarkLeaflet, rmfLight, AlertDialog, gridZhCN } from 'react-components';
import { loadSettings, saveSettings, Settings, ThemeMode } from '../settings';
import { AppController, AppControllerContext, SettingsContext } from './app-contexts';
import AppBar from './appbar';
import { AlertStore } from './alert-store';

const DefaultAlertDuration = 2000;
const defaultTheme = createTheme({}, zhCN, gridZhCN);

/**
 * Contains various components that are essential to the app and provides contexts to control them.
 * Components include:
 *
 * - Settings
 * - Alerts
 *
 * Also provides `AppControllerContext` to allow children components to control them.
 */
export function AppBase({ children }: React.PropsWithChildren<{}>): JSX.Element | null {
  const [settings, setSettings] = React.useState(() => loadSettings());
  const [showAlert, setShowAlert] = React.useState(false);
  const [lowResolutionAlert, setLowResolutionAlert] = React.useState(false);
  const [alertSeverity, setAlertSeverity] = React.useState<AlertProps['severity']>('error');
  const [alertMessage, setAlertMessage] = React.useState('');
  const [alertDuration, setAlertDuration] = React.useState(DefaultAlertDuration);
  const [extraAppbarIcons, setExtraAppbarIcons] = React.useState<React.ReactNode>(null);

  const theme = React.useMemo(() => {
    switch (settings.themeMode) {
      case ThemeMode.RmfLight:
        return createTheme(rmfLight, zhCN, gridZhCN);
      case ThemeMode.RmfDark:
        return createTheme(rmfDark, zhCN, gridZhCN);
      default:
        return defaultTheme;
    }
  }, [settings.themeMode]);

  const updateSettings = React.useCallback((newSettings: Settings) => {
    saveSettings(newSettings);
    setSettings(newSettings);
  }, []);

  const appController = React.useMemo<AppController>(
    () => ({
      updateSettings,
      showAlert: (severity, message, autoHideDuration) => {
        setAlertSeverity(severity);
        setAlertMessage(message);
        setShowAlert(true);
        setAlertDuration(autoHideDuration || DefaultAlertDuration);
      },
      setExtraAppbarIcons,
    }),
    [updateSettings],
  );

  React.useEffect(() => {
    const checkSize = () => {
      if (window.innerWidth < 640) {
        setLowResolutionAlert(true);
      }
    };
    checkSize();
    window.addEventListener('resize', checkSize);
  }, []);

  const dismissDisplayAlert = () => {
    setLowResolutionAlert(false);
  };

  const lowResolutionDisplayAlert = () => {
    return (
      <AlertDialog
        key="display-alert"
        onDismiss={dismissDisplayAlert}
        title="检测到显示分辨率较低"
        alertContents={[
          {
            title: '当前分辨率',
            value: `${window.innerWidth} x ${window.innerHeight}`,
          },
          {
            title: '最低建议分辨率',
            value: '1920 x 1080',
          },
          {
            title: '提示信息',
            value:
              '为确保界面正常显示，请降低浏览器缩放比例 ' +
              '（Ctrl + 减号）或调整显示设置， ' +
              '也可以使用分辨率更高的显示设备。',
          },
        ]}
        backgroundColor={theme.palette.background.default}
      />
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {settings.themeMode === ThemeMode.RmfDark && <GlobalStyles styles={rmfDarkLeaflet} />}
      <SettingsContext.Provider value={settings}>
        <AppControllerContext.Provider value={appController}>
          <AlertStore />
          {lowResolutionAlert && lowResolutionDisplayAlert()}
          <Grid
            className="of-shell"
            data-theme={settings.themeMode}
            container
            direction="column"
            style={{ width: '100%', height: '100%' }}
            wrap="nowrap"
          >
            <AppBar extraToolbarItems={extraAppbarIcons} />
            {children}
            {/* TODO: Support stacking of alerts */}
            <Snackbar
              open={showAlert}
              message={alertMessage}
              onClose={() => setShowAlert(false)}
              autoHideDuration={alertDuration}
            >
              <Alert
                onClose={() => setShowAlert(false)}
                severity={alertSeverity}
                sx={{ width: '100%' }}
              >
                {alertMessage}
              </Alert>
            </Snackbar>
          </Grid>
        </AppControllerContext.Provider>
      </SettingsContext.Provider>
    </ThemeProvider>
  );
}
