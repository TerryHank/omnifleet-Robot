declare enum AppEvent {
    APP_INIT = "Studio: App Initialized",
    DIALOG_SELECT_VIEW = "Studio: Dialog View Selected",
    DIALOG_CLOSE = "Studio: Dialog Closed",
    DIALOG_CLICK_CTA = "Studio: Dialog CTA Clicked",
    APP_BAR_CLICK_CTA = "Studio: App Bar CTA CLicked",
    TOUR_PROMPT_SHOWN = "Studio: New UI Tour prompt shown",
    TOUR_STARTED = "Studio: New UI Tour started",
    TOUR_BACK = "Studio: New UI Tour step back",
    TOUR_NEXT = "Studio: New UI Tour step next",
    TOUR_COMPLETED = "Studio: New UI Tour completed",
    TOUR_DISMISSED = "Studio: New UI Tour dismissed",
    APP_MENU_CLICK = "Studio: App Menu Clicked",
    HELP_MENU_CLICK_CTA = "Studio: Help Menu CTA Clicked",
    PLAYER_CONSTRUCTED = "Studio: Player Constructed",
    LAYOUT_UPDATE = "Studio: Layout Updated",
    LAYOUT_CREATE = "Studio: Layout Created",
    LAYOUT_DUPLICATE = "Studio: Layout Duplicated",
    LAYOUT_RENAME = "Studio: Layout Renamed",
    LAYOUT_DELETE = "Studio: Layout Deleted",
    LAYOUT_SELECT = "Studio: Layout Selected",
    LAYOUT_IMPORT = "Studio: Layout Imported",
    LAYOUT_EXPORT = "Studio: Layout Exported",
    LAYOUT_SHARE = "Studio: Layout Shared",
    LAYOUT_OVERWRITE = "Studio: Layout Overwritten",
    LAYOUT_REVERT = "Studio: Layout Reverted",
    LAYOUT_MAKE_PERSONAL_COPY = "Studio: Layout Personal Copy Made",
    PANEL_ADD = "Studio: Panel Added",
    PANEL_DELETE = "Studio: Panel Deleted",
    VARIABLE_ADD = "Studio: Variable Added",
    VARIABLE_DELETE = "Studio: Variable Deleted",
    IMAGE_DOWNLOAD = "Studio: Image Downloaded",
    EXTENSION_INSTALL = "Studio: Extension Installed",
    EXTENSION_UNINSTALL = "Studio: Extension Uninstalled",
    EXPERIMENTAL_FEATURE_TOGGLE = "Studio: Experimental Feature Toggled",
    USER_OBSERVATION = "Studio: User Makes Observation",
    USER_ACTIVATION = "Studio: User Activated"
}
interface IAnalytics {
    logEvent(event: AppEvent, data?: {
        [key: string]: unknown;
    }): void | Promise<void>;
}
export { AppEvent };
export default IAnalytics;
