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
};
export default _default;
export declare const CameraInfoRender: StoryObj;
export declare const CameraInfoRenderChinese: {
    parameters: {
        colorScheme: string;
        forceLanguage: string;
    };
    decorators?: import("@storybook/types").DecoratorFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}> | import("@storybook/types").DecoratorFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}>[] | undefined;
    args?: (Partial<{}> & {}) | undefined;
    argTypes?: Partial<import("@storybook/types").ArgTypes<{}>> | undefined;
    loaders?: import("@storybook/types").LoaderFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}> | import("@storybook/types").LoaderFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}>[] | undefined;
    render?: import("@storybook/types").ArgsStoryFn<import("@storybook/react/dist/types-0fc72a6d").R, {}> | undefined;
    name?: string | undefined;
    storyName?: string | undefined;
    play?: import("@storybook/types").PlayFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}> | undefined;
    tags?: string[] | undefined;
    story?: Omit<import("@storybook/types").StoryAnnotations<import("@storybook/react/dist/types-0fc72a6d").R, {}, Partial<{}>>, "story"> | undefined;
};
export declare const CameraInfoRenderJapanese: {
    parameters: {
        colorScheme: string;
        forceLanguage: string;
    };
    decorators?: import("@storybook/types").DecoratorFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}> | import("@storybook/types").DecoratorFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}>[] | undefined;
    args?: (Partial<{}> & {}) | undefined;
    argTypes?: Partial<import("@storybook/types").ArgTypes<{}>> | undefined;
    loaders?: import("@storybook/types").LoaderFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}> | import("@storybook/types").LoaderFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}>[] | undefined;
    render?: import("@storybook/types").ArgsStoryFn<import("@storybook/react/dist/types-0fc72a6d").R, {}> | undefined;
    name?: string | undefined;
    storyName?: string | undefined;
    play?: import("@storybook/types").PlayFunction<import("@storybook/react/dist/types-0fc72a6d").R, {}> | undefined;
    tags?: string[] | undefined;
    story?: Omit<import("@storybook/types").StoryAnnotations<import("@storybook/react/dist/types-0fc72a6d").R, {}, Partial<{}>>, "story"> | undefined;
};
