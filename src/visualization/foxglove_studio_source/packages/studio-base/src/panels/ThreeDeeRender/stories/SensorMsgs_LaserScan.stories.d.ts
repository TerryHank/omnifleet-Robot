/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: {} | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: Record<string, unknown>;
        saveConfig: import("../../../types/panels").SaveConfig<Record<string, unknown>>;
        onDownloadImage?: ((blob: Blob, fileName: string) => void) | undefined;
        debugPicking?: boolean | undefined;
    }, "config" | "saveConfig">> & import("../../../components/Panel").PanelStatics<{}>;
    parameters: {
        colorScheme: string;
    };
};
export default _default;
declare function SensorMsgs_LaserScan({ time, rangeMin, rangeMax, settings, }: {
    time?: number;
    rangeMin?: number;
    rangeMax?: number;
    settings: Record<string, unknown>;
}): JSX.Element;
export declare const Square: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
export declare const Size20: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
export declare const FlatColor: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
export declare const CustomGradient: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
export declare const RangeLimits: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
export declare const Time0: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
export declare const Time5: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
export declare const Time10: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
export declare const ComparisonWithPointCloudColors: StoryObj<Parameters<typeof SensorMsgs_LaserScan>[0]>;
