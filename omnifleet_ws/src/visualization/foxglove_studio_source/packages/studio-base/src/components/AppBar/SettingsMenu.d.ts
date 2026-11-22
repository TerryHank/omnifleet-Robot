/// <reference types="react" />
import { PopoverPosition, PopoverReference } from "@mui/material";
type SettingsMenuProps = {
    handleClose: () => void;
    anchorEl?: HTMLElement;
    anchorReference?: PopoverReference;
    anchorPosition?: PopoverPosition;
    disablePortal?: boolean;
    open: boolean;
};
export declare function SettingsMenu({ anchorEl, anchorReference, anchorPosition, disablePortal, handleClose, open, }: SettingsMenuProps): JSX.Element;
export {};
