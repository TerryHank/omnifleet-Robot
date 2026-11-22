/// <reference types="react" />
import { PopoverPosition, PopoverReference } from "@mui/material";
export type AppMenuProps = {
    handleClose: () => void;
    anchorEl?: HTMLElement;
    anchorReference?: PopoverReference;
    anchorPosition?: PopoverPosition;
    disablePortal?: boolean;
    open: boolean;
};
export declare function AppMenu(props: AppMenuProps): JSX.Element;
