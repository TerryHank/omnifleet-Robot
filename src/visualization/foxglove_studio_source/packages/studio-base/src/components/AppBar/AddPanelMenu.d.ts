/// <reference types="react" />
import { PopoverPosition, PopoverReference } from "@mui/material";
type AddPanelProps = {
    anchorEl?: HTMLElement;
    anchorPosition?: PopoverPosition;
    anchorReference?: PopoverReference;
    disablePortal?: boolean;
    handleClose: () => void;
    open: boolean;
};
export declare function AddPanelMenu(props: AddPanelProps): JSX.Element;
export {};
