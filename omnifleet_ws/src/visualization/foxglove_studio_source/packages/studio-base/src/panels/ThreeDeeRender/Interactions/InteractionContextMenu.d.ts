/// <reference types="react" />
import { MenuProps } from "@mui/material";
import { MouseEventObject } from "../camera";
type ClickedPosition = {
    clientX: number;
    clientY: number;
};
type Props = {
    clickedPosition: ClickedPosition;
    clickedObjects: MouseEventObject[];
    onClose: MenuProps["onClose"];
    selectObject: (arg0?: MouseEventObject) => void;
};
export declare function InteractionContextMenu({ clickedObjects, clickedPosition, onClose, selectObject, }: Props): JSX.Element;
export {};
