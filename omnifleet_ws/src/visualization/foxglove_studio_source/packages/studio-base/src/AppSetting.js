// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export var AppSetting;
(function (AppSetting) {
    // General
    AppSetting["COLOR_SCHEME"] = "colorScheme";
    AppSetting["TIMEZONE"] = "timezone";
    AppSetting["TIME_FORMAT"] = "time.format";
    AppSetting["MESSAGE_RATE"] = "messageRate";
    AppSetting["UPDATES_ENABLED"] = "updates.enabled";
    AppSetting["LANGUAGE"] = "language";
    // ROS
    AppSetting["ROS_PACKAGE_PATH"] = "ros.ros_package_path";
    // Experimental features
    AppSetting["SHOW_DEBUG_PANELS"] = "showDebugPanels";
    // Miscellaneous
    AppSetting["HIDE_SIGN_IN_PROMPT"] = "hideSignInPrompt";
    AppSetting["LAUNCH_PREFERENCE"] = "launchPreference";
    AppSetting["SHOW_OPEN_DIALOG_ON_STARTUP"] = "ui.open-dialog-startup";
    AppSetting["ENABLE_UNIFIED_NAVIGATION"] = "ui.new-app-menu";
    // Dev only
    AppSetting["ENABLE_LAYOUT_DEBUGGING"] = "enableLayoutDebugging";
})(AppSetting || (AppSetting = {}));
