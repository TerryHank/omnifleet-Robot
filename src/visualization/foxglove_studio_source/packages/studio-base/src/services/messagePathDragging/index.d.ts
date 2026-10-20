import { CSSProperties } from "react";
import { ConnectDragPreview, ConnectDragSource, ConnectDropTarget } from "react-dnd";
import { MessagePathDropConfig } from "@foxglove/studio-base/components/PanelExtensionAdapter";
import { MessagePathDragParams } from "./types";
/**
 * Use this to create a drag source for message paths that can be dropped onto target components
 * that use `useMessagePathDrop()`.
 */
export declare function useMessagePathDrag({ item, selected }: MessagePathDragParams): {
    connectDragSource: ConnectDragSource;
    connectDragPreview: ConnectDragPreview;
    cursor?: CSSProperties["cursor"];
    isDragging: boolean;
    draggedItemCount: number;
};
/**
 * Use this to create a drop target accepting message paths dragged from components that use
 * `useMessagePathDrag()`.
 */
export declare function useMessagePathDrop(): {
    /** True if the target supports dragging (a config is set) and a drag has started */
    isDragging: boolean;
    isOver: boolean;
    isValidTarget: boolean;
    dropMessage: string | undefined;
    connectMessagePathDropTarget: ConnectDropTarget;
    setMessagePathDropConfig: (config: MessagePathDropConfig | undefined) => void;
};
