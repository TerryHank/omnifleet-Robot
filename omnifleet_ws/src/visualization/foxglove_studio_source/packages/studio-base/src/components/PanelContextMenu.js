import { jsx as _jsx } from "react/jsx-runtime";
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { Divider, Menu, MenuItem } from "@mui/material";
import { useCallback, useEffect, useRef, useState } from "react";
import { PANEL_ROOT_CLASS_NAME } from "@foxglove/studio-base/components/PanelRoot";
/**
 * This is a convenience component for attaching a context menu to a panel. It
 * must be a child of a Panel component to work.
 */
function PanelContextMenuComponent(props) {
    const { getItems } = props;
    const rootRef = useRef(ReactNull);
    const [position, setPosition] = useState();
    const handleClose = useCallback(() => {
        setPosition(undefined);
    }, []);
    const [items, setItems] = useState([]);
    useEffect(() => {
        const parent = rootRef.current?.closest(`.${PANEL_ROOT_CLASS_NAME}`);
        if (!parent) {
            return;
        }
        // Trigger the menu when the right mouse button is released, but not if the mouse moved in
        // between press & release
        let rightClickState = "none";
        const handleMouseUp = (event) => {
            if (event.button === 2 && rightClickState === "down") {
                setPosition({ x: event.clientX, y: event.clientY });
                setItems(getItems());
                rightClickState = "none";
            }
        };
        const handleMouseMove = (_event) => {
            rightClickState = "canceled";
        };
        const handleMouseDown = (event) => {
            if (event.button === 2) {
                rightClickState = "down";
            }
        };
        const handleContextMenu = (event) => {
            event.preventDefault();
        };
        parent.addEventListener("mousedown", handleMouseDown);
        parent.addEventListener("mousemove", handleMouseMove);
        parent.addEventListener("mouseup", handleMouseUp);
        parent.addEventListener("contextmenu", handleContextMenu);
        return () => {
            parent.removeEventListener("mousedown", handleMouseDown);
            parent.removeEventListener("mousemove", handleMouseMove);
            parent.removeEventListener("mouseup", handleMouseUp);
            parent.removeEventListener("contextmenu", handleContextMenu);
        };
    }, [getItems]);
    return (_jsx("div", { ref: rootRef, onContextMenu: (event) => {
            event.preventDefault();
        }, children: _jsx(Menu, { open: position != undefined, onClose: handleClose, anchorReference: "anchorPosition", anchorPosition: position ? { top: position.y, left: position.x } : undefined, MenuListProps: {
                dense: true,
            }, children: items.map((item, index) => {
                if (item.type === "divider") {
                    return _jsx(Divider, { variant: "middle" }, `divider_${index}`);
                }
                return (_jsx(MenuItem, { onClick: () => {
                        handleClose();
                        item.onclick();
                    }, disabled: item.disabled, children: item.label }, `item_${index}_${item.label}`));
            }) }) }));
}
export const PanelContextMenu = React.memo(PanelContextMenuComponent);
