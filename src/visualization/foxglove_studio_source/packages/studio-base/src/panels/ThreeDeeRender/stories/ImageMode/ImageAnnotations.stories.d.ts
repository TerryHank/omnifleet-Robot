/// <reference types="react" />
import { StoryObj } from "@storybook/react";
import { ImageAnnotations } from "@foxglove/schemas";
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
export declare const Annotations: StoryObj;
export declare const AnnotationsPicking: StoryObj;
export declare const AnnotationsWithoutCalibration: StoryObj;
export declare const MessageConverterSupport: StoryObj;
export declare const AnnotationsUpdate: StoryObj;
type UpdateLineArgs = {
    messages: readonly Partial<ImageAnnotations>[];
};
/** Vertex colors remain enabled, but colors change */
export declare const UpdateLineChangeVertexColors: StoryObj<UpdateLineArgs>;
/** Change from vertex colors off to on */
export declare const UpdateLineEnableVertexColors: StoryObj<UpdateLineArgs>;
export declare const OddLengthLineList: StoryObj;
export declare const LinesWithAndWithoutVertexColors: StoryObj;
type SyncAnnotationsStoryArgs = {
    status: "waiting" | "ready";
    hasCalibrationTopic: boolean;
};
export declare const SyncAnnotationsWaitingWithCalibration: StoryObj<SyncAnnotationsStoryArgs>;
export declare const SyncAnnotationsWaitingWithoutCalibration: StoryObj<SyncAnnotationsStoryArgs>;
export declare const SyncAnnotationsReadyWithCalibration: StoryObj<SyncAnnotationsStoryArgs>;
export declare const SyncAnnotationsReadyWithoutCalibration: StoryObj<SyncAnnotationsStoryArgs>;
