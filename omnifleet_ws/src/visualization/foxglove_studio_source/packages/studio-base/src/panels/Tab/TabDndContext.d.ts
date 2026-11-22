/// <reference types="react" />
export declare const TAB_DRAG_TYPE = "TAB";
export type DraggingTabItem = {
    type: typeof TAB_DRAG_TYPE;
    tabIndex: number;
    panelId: string;
};
export type DraggingTabPanelState = {
    item?: DraggingTabItem;
    isOver: boolean;
};
export type TabActions = {
    addTab: () => void;
    removeTab: (tabIndex: number) => void;
    selectTab: (tabIndex: number) => void;
    setTabTitle: (tabIndex: number, title: string) => void;
};
export declare const TabDndContext: import("react").Context<{
    preventTabDrop: boolean;
}>;
