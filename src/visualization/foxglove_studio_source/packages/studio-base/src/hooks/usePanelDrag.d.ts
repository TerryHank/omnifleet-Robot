import { ConnectDragSource, ConnectDragPreview } from "react-dnd";
export default function usePanelDrag(props: {
    tabId?: string;
    panelId?: string;
    onDragStart?: () => void;
    onDragEnd?: () => void;
}): [ConnectDragSource, ConnectDragPreview];
