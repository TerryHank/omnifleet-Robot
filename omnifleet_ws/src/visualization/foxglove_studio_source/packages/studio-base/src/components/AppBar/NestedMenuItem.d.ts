import { PropsWithChildren } from "react";
import { AppBarMenuItem } from "./types";
export declare function NestedMenuItem(props: PropsWithChildren<{
    id?: string;
    items: AppBarMenuItem[];
    open: boolean;
    onPointerEnter: (itemId: string) => void;
}>): JSX.Element;
