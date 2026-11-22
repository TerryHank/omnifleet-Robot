// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
var AppEvent;
(function (AppEvent) {
    AppEvent["APP_INIT"] = "Studio: App Initialized";
    // Dialog events
    AppEvent["DIALOG_SELECT_VIEW"] = "Studio: Dialog View Selected";
    AppEvent["DIALOG_CLOSE"] = "Studio: Dialog Closed";
    AppEvent["DIALOG_CLICK_CTA"] = "Studio: Dialog CTA Clicked";
    // App Bar events
    AppEvent["APP_BAR_CLICK_CTA"] = "Studio: App Bar CTA CLicked";
    // Tour events
    AppEvent["TOUR_PROMPT_SHOWN"] = "Studio: New UI Tour prompt shown";
    AppEvent["TOUR_STARTED"] = "Studio: New UI Tour started";
    AppEvent["TOUR_BACK"] = "Studio: New UI Tour step back";
    AppEvent["TOUR_NEXT"] = "Studio: New UI Tour step next";
    AppEvent["TOUR_COMPLETED"] = "Studio: New UI Tour completed";
    AppEvent["TOUR_DISMISSED"] = "Studio: New UI Tour dismissed";
    // App Menu events
    AppEvent["APP_MENU_CLICK"] = "Studio: App Menu Clicked";
    // Help Menu events
    AppEvent["HELP_MENU_CLICK_CTA"] = "Studio: Help Menu CTA Clicked";
    // Player events
    AppEvent["PLAYER_CONSTRUCTED"] = "Studio: Player Constructed";
    // Layout events
    AppEvent["LAYOUT_UPDATE"] = "Studio: Layout Updated";
    AppEvent["LAYOUT_CREATE"] = "Studio: Layout Created";
    AppEvent["LAYOUT_DUPLICATE"] = "Studio: Layout Duplicated";
    AppEvent["LAYOUT_RENAME"] = "Studio: Layout Renamed";
    AppEvent["LAYOUT_DELETE"] = "Studio: Layout Deleted";
    AppEvent["LAYOUT_SELECT"] = "Studio: Layout Selected";
    AppEvent["LAYOUT_IMPORT"] = "Studio: Layout Imported";
    AppEvent["LAYOUT_EXPORT"] = "Studio: Layout Exported";
    AppEvent["LAYOUT_SHARE"] = "Studio: Layout Shared";
    AppEvent["LAYOUT_OVERWRITE"] = "Studio: Layout Overwritten";
    AppEvent["LAYOUT_REVERT"] = "Studio: Layout Reverted";
    AppEvent["LAYOUT_MAKE_PERSONAL_COPY"] = "Studio: Layout Personal Copy Made";
    // Panel events
    AppEvent["PANEL_ADD"] = "Studio: Panel Added";
    AppEvent["PANEL_DELETE"] = "Studio: Panel Deleted";
    // Variable events
    AppEvent["VARIABLE_ADD"] = "Studio: Variable Added";
    AppEvent["VARIABLE_DELETE"] = "Studio: Variable Deleted";
    // Image events
    AppEvent["IMAGE_DOWNLOAD"] = "Studio: Image Downloaded";
    // Extension events
    AppEvent["EXTENSION_INSTALL"] = "Studio: Extension Installed";
    AppEvent["EXTENSION_UNINSTALL"] = "Studio: Extension Uninstalled";
    // Experimental features
    AppEvent["EXPERIMENTAL_FEATURE_TOGGLE"] = "Studio: Experimental Feature Toggled";
    // User engagement
    AppEvent["USER_OBSERVATION"] = "Studio: User Makes Observation";
    AppEvent["USER_ACTIVATION"] = "Studio: User Activated";
})(AppEvent || (AppEvent = {}));
export { AppEvent };
