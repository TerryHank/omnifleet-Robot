/// <reference types="react" />
export type AppConfigurationValue = string | number | boolean | undefined;
export type ChangeHandler = (newValue: AppConfigurationValue) => void;
export interface IAppConfiguration {
    get(key: string): AppConfigurationValue;
    set(key: string, value: AppConfigurationValue): Promise<void>;
    addChangeListener(key: string, cb: ChangeHandler): void;
    removeChangeListener(key: string, cb: ChangeHandler): void;
}
declare const AppConfigurationContext: import("react").Context<IAppConfiguration | undefined>;
export declare function useAppConfiguration(): IAppConfiguration;
export default AppConfigurationContext;
