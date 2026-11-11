import { AppConfigurationValue } from "@foxglove/studio-base/context/AppConfigurationContext";
/**
 * Load a value from app configuration and provide a function to change it
 * This function behaves similarly to useState for a given app configuration key.
 */
export declare function useAppConfigurationValue<T extends AppConfigurationValue>(key: string): [value: T | undefined, setter: (value?: T) => Promise<void>];
