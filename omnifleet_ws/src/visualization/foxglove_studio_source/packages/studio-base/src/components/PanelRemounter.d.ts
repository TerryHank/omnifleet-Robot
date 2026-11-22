import { ReactNode } from "react";
/**
 * Wrapper component used to force-remount the panel when key properties like the tabId
 * or settings sequence number change.
 */
export declare function PanelRemounter({ children, id, tabId, }: {
    children: ReactNode;
    id: string;
    tabId: undefined | string;
}): JSX.Element;
