/// <reference types="react" />
import { BadgeProps } from "@mui/material";
export type SidebarItem = {
    title: string;
    component: React.ComponentType;
    badge?: {
        color: BadgeProps["color"];
        count: number;
    };
};
export declare function Sidebar<K extends string>({ items, anchor, onClose, activeTab, setActiveTab, }: {
    items: Map<K, SidebarItem>;
    anchor: "right" | "left";
    onClose: () => void;
    activeTab: K | undefined;
    setActiveTab: (newValue: K) => void;
}): JSX.Element;
