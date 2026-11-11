/// <reference types="react" />
import { StoryObj } from "@storybook/react";
declare const _default: {
    title: string;
    component: import("react").ComponentType<{
        childId?: string | undefined;
        overrideConfig?: Record<string, unknown> | undefined;
        tabId?: string | undefined;
    } & Omit<{
        config: Record<string, unknown>;
        saveConfig: import("../../../../types/panels").SaveConfig<Record<string, unknown>>;
        onDownloadImage?: ((blob: Blob, fileName: string) => void) | undefined;
        debugPicking?: boolean | undefined;
    }, "config" | "saveConfig">> & import("../../../../components/Panel").PanelStatics<Record<string, unknown>>;
    parameters: {
        colorScheme: string;
    };
};
export default _default;
type BaseStoryProps = {
    rotation: 0 | 90 | 180 | 270;
    flipHorizontal: boolean;
    flipVertical: boolean;
};
export declare const PanZoom: StoryObj<BaseStoryProps & {
    dx: number;
    dy: number;
    panX: number;
    panY: number;
}>;
export declare const PanZoomFlipH: typeof PanZoom;
export declare const PanZoomFlipV: typeof PanZoom;
export declare const PanZoom90: typeof PanZoom;
export declare const PanZoom90FlipH: typeof PanZoom;
export declare const PanZoom90FlipV: typeof PanZoom;
export declare const PanZoom180: typeof PanZoom;
export declare const PanZoom270: typeof PanZoom;
