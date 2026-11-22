import { StoryFn, StoryObj } from "@storybook/react";
import { PointCloud2 } from "@foxglove/studio-base/types/Messages";
export declare const POINT_CLOUD_MESSAGE: PointCloud2;
export declare const POINT_CLOUD_WITH_ADDITIONAL_FIELDS: PointCloud2;
declare const _default: {
    title: string;
    parameters: {
        chromatic: {
            viewport: {
                width: number;
                height: number;
            };
        };
        colorScheme: string;
    };
    excludeStories: string[];
    decorators: ((Story: StoryFn) => JSX.Element)[];
};
export default _default;
export declare const Default: StoryObj;
export declare const PointCloud: StoryObj;
