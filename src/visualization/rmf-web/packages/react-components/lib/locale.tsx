import { LocalizationProvider as MuiLocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { zhCN as pickerZhCN } from '@mui/x-date-pickers/locales';
import { zhCN } from 'date-fns/locale';
import React from 'react';

export { zhCN as gridZhCN } from '@mui/x-data-grid';
export const LocaleContext = React.createContext<string | null>(null);

export const LocalizationProvider: React.FC<React.PropsWithChildren> = ({ children }) => (
  <MuiLocalizationProvider
    dateAdapter={AdapterDateFns}
    adapterLocale={zhCN}
    localeText={{
      ...pickerZhCN.components.MuiLocalizationProvider.defaultProps.localeText,
      datePickerDefaultToolbarTitle: '选择日期',
      dateTimePickerDefaultToolbarTitle: '选择日期和时间',
      timePickerDefaultToolbarTitle: '选择时间',
      dateRangePickerDefaultToolbarTitle: '选择日期范围',
      inputModeToggleButtonAriaLabel: (keyboardOpen) =>
        keyboardOpen ? '切换到日历选择' : '切换到文本输入',
      clockLabelText: (view, time, adapter) =>
        `选择${{ hours: '小时', minutes: '分钟', seconds: '秒' }[view]}。${
          time === null ? '未选择时间' : `已选择 ${adapter.format(time, 'fullTime')}`
        }`,
    }}
  >
    {children}
  </MuiLocalizationProvider>
);

export default LocalizationProvider;
