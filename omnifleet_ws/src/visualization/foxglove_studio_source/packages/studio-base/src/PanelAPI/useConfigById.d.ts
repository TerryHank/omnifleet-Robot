import { SaveConfig } from "@foxglove/studio-base/types/panels";
/**
 * Like `useConfig`, but for a specific panel id. This generally shouldn't be used by panels
 * directly, but is for use in internal code that's running outside of regular context providers.
 */
export default function useConfigById<Config extends Record<string, unknown>>(panelId: string | undefined): [Config | undefined, SaveConfig<Config>];
