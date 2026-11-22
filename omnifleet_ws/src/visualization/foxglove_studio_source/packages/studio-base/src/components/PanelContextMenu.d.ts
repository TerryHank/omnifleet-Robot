/// <reference types="react" />
import { Immutable } from "@foxglove/studio";
/**
 * Types of items that can be included in a context menu. Either a clickable item
 * or a divider.
 */
export type PanelContextMenuItem = {
    /** Type of selectable menu items. */
    type: "item";
    /** True if the item should be shown but disabled. */
    disabled?: boolean;
    /** Label shown for the menu item. */
    label: string;
    /** Callback triggered by clicking the item. */
    onclick: () => void;
} | {
    /** Type of item dividers. */
    type: "divider";
};
type PanelContextMenuProps = {
    /** @returns List of menu items */
    getItems: () => Immutable<PanelContextMenuItem[]>;
};
/**
 * This is a convenience component for attaching a context menu to a panel. It
 * must be a child of a Panel component to work.
 */
declare function PanelContextMenuComponent(props: PanelContextMenuProps): JSX.Element;
export declare const PanelContextMenu: import("react").MemoExoticComponent<typeof PanelContextMenuComponent>;
export {};
