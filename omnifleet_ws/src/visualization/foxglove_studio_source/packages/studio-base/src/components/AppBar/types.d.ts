import { MouseEventHandler, ReactNode } from "react";
/**
 * Represents an item in the app bar menus.
 */
export type AppBarMenuItem = {
    type: "item";
    label: ReactNode;
    key: string;
    disabled?: boolean;
    shortcut?: string;
    onClick?: MouseEventHandler<HTMLElement>;
    external?: boolean;
    icon?: ReactNode;
} | {
    type: "subheader";
    label: ReactNode;
    key: string;
} | {
    type: "divider";
};
