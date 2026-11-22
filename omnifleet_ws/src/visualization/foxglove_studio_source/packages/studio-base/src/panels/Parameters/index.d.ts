/// <reference types="react" />
declare const _default: import("react").ComponentType<{
    childId?: string | undefined;
    overrideConfig?: {
        title: string;
    } | undefined;
    tabId?: string | undefined;
} & Omit<{
    config: {
        title: string;
    };
    saveConfig: import("../../types/panels").SaveConfig<{
        title: string;
    }>;
}, "config" | "saveConfig">> & import("@foxglove/studio-base/components/Panel").PanelStatics<{
    title: string;
}>;
export default _default;
