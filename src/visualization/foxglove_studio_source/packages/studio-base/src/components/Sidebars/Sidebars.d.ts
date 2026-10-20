import { PropsWithChildren } from "react";
import { SidebarItem } from "./Sidebar";
import "react-mosaic-component/react-mosaic-component.css";
type SidebarProps<LeftKey, RightKey> = PropsWithChildren<{
    leftItems: Map<LeftKey, SidebarItem>;
    selectedLeftKey: LeftKey | undefined;
    onSelectLeftKey: (key: LeftKey | undefined) => void;
    leftSidebarSize: number | undefined;
    setLeftSidebarSize: (size: number | undefined) => void;
    rightItems: Map<RightKey, SidebarItem>;
    selectedRightKey: RightKey | undefined;
    onSelectRightKey: (key: RightKey | undefined) => void;
    rightSidebarSize: number | undefined;
    setRightSidebarSize: (size: number | undefined) => void;
}>;
export declare function Sidebars<LeftKey extends string, RightKey extends string>(props: SidebarProps<LeftKey, RightKey>): JSX.Element;
export {};
