import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Menu, MenuItem } from "@mui/material";
import { useCallback } from "react";
const getInstanceObj = (marker, idx) => {
    if (marker == undefined) {
        return;
    }
    return marker.metadataByIndex?.[idx];
};
const getObject = (selectedObject) => {
    const object = (selectedObject?.instanceIndex != undefined &&
        selectedObject.object.metadataByIndex != undefined &&
        getInstanceObj(selectedObject.object, selectedObject.instanceIndex) != undefined) ||
        selectedObject?.object;
    return object;
};
function InteractionContextMenuItem({ interactiveObject, selectObject, }) {
    const object = getObject(interactiveObject);
    const selectItemObject = useCallback(() => {
        selectObject(interactiveObject);
    }, [interactiveObject, selectObject]);
    return (_jsx(MenuItem, { "data-test": "InteractionContextMenuItem", onClick: selectItemObject, children: object.interactionData?.topic }));
}
export function InteractionContextMenu({ clickedObjects = [], clickedPosition = { clientX: 0, clientY: 0 }, onClose, selectObject, }) {
    return (_jsx(Menu, { open: true, onClose: onClose, anchorReference: "anchorPosition", anchorPosition: {
            top: clickedPosition.clientY,
            left: clickedPosition.clientX,
        }, MenuListProps: {
            dense: true,
        }, children: clickedObjects.map((interactiveObject, index) => (_jsx(InteractionContextMenuItem, { interactiveObject: interactiveObject, selectObject: selectObject }, index))) }));
}
