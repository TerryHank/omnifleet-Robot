/// <reference types="react" />
import { CustomWindowControlsProps } from "./CustomWindowControls";
export type AppBarProps = CustomWindowControlsProps & {
    leftInset?: number;
    onDoubleClick?: () => void;
    debugDragRegion?: boolean;
};
export declare function AppBar(props: AppBarProps): JSX.Element;
