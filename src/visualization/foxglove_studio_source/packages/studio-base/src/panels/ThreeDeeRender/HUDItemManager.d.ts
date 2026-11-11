export type HUDItem = {
    /** Unique identifier for the item. Adding a message with the same id twice will result in a no-op */
    id: string;
    /** Designate what group this belongs to. Allows items to be cleared by group.
     * Would allow scene extensions to only clear their own items when applicable.
     */
    group: string;
    /** Function to return message content to show on HUD */
    getMessage: () => string;
    /** Display type */
    displayType: "empty" | "notice";
};
/** Priority list of HUD item ids. IDs earlier in the list should be shown before items later in the list.
 * This list is reversed before use to take advantage of `indexOf` for items that aren't included being lower priority than items on the list.
 * IDs not in this list will be shown after all items in this list.
 */
export declare const HUD_ID_PRIORITIES: string[];
export declare class HUDItemManager {
    #private;
    constructor(onChange: () => void);
    addHUDItem(item: HUDItem): void;
    removeHUDItem(id: string): void;
    removeGroup(group: string): void;
    displayIfTrue(value: boolean, hudItem: HUDItem): void;
    /** Returns list of HUD items in ascending priority order.
     * High priority items will be last in the list.
     */
    getHUDItems(): HUDItem[];
    clear(): void;
}
