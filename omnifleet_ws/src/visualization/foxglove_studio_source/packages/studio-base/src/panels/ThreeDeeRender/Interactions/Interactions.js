import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2018-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import { Cursor20Regular } from "@fluentui/react-icons";
import { Typography } from "@mui/material";
import ExpandingToolbar, { ToolGroup, ToolGroupFixedSizePane, } from "@foxglove/studio-base/components/ExpandingToolbar";
import ObjectDetails from "./ObjectDetails";
import TopicLink from "./TopicLink";
export const OBJECT_TAB_TYPE = "Selected object";
const InteractionsBaseComponent = React.memo(function InteractionsBaseComponent({ addPanel, selectedObject, interactionsTabType, onShowTopicSettings, setInteractionsTabType, timezone, }) {
    const selectedInteractionData = selectedObject?.object.interactionData;
    const originalMessage = selectedInteractionData?.originalMessage;
    const instanceDetails = selectedInteractionData?.instanceDetails;
    return (_jsx(ExpandingToolbar, { tooltip: "\u68C0\u67E5\u5BF9\u8C61", icon: _jsx(Cursor20Regular, {}), selectedTab: interactionsTabType, onSelectTab: (newSelectedTab) => {
            setInteractionsTabType(newSelectedTab);
        }, children: _jsx(ToolGroup, { name: OBJECT_TAB_TYPE, children: _jsx(ToolGroupFixedSizePane, { children: originalMessage ? (_jsxs(_Fragment, { children: [selectedInteractionData.topic && (_jsx(TopicLink, { addPanel: addPanel, onShowTopicSettings: onShowTopicSettings, topic: selectedInteractionData.topic })), instanceDetails ? (_jsx(ObjectDetails, { selectedObject: instanceDetails, timezone: timezone })) : (_jsx(_Fragment, {})), _jsx(ObjectDetails, { selectedObject: originalMessage, interactionData: selectedInteractionData, timezone: timezone })] })) : (_jsx(Typography, { variant: "body2", color: "text.disabled", gutterBottom: true, children: "Click an object in the 3D view to select it." })) }) }) }));
});
// Wrap the Interactions so that we don't rerender every time any part of the PanelContext config changes, but just the
// one value that we care about.
export default function Interactions(props) {
    return _jsx(InteractionsBaseComponent, { ...props });
}
