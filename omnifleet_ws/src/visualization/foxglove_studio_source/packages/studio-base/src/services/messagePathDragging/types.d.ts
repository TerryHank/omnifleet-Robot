import { DraggedMessagePath } from "@foxglove/studio-base/components/PanelExtensionAdapter";
export type MessagePathDragParams = {
    /**
     * The item represented by the component that is using `useMessagePathDrag`. If no items are
     * selected and a drag begins on this component, this will be used as the drag item.
     */
    item: DraggedMessagePath;
    /**
     * Whether this item is currently selected.
     */
    selected: boolean;
};
