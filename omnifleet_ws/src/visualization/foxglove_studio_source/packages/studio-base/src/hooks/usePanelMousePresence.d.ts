import { MutableRefObject } from "react";
/**
 * Tracks the presence of the mouse in the parent panel.
 *
 * @param ref The element to hide and show on panel hove
 * @returns True if the mouse is currently within the parent panel.
 */
export declare function usePanelMousePresence(ref: MutableRefObject<HTMLElement | ReactNull>): boolean;
