/// <reference types="react" />
import { MenuProps } from "@mui/material";
import { DraggedMessagePath } from "@foxglove/studio-base/components/PanelExtensionAdapter";
export declare function ContextMenu(props: {
    messagePaths: DraggedMessagePath[];
    anchorPosition: NonNullable<MenuProps["anchorPosition"]>;
    onClose: () => void;
}): JSX.Element;
