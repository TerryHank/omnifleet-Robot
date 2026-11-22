import Cytoscape from "cytoscape";
import { MutableRefObject } from "react";
export interface GraphMutation {
    fit: () => void;
    resetUserPanZoom: () => void;
}
type Props = {
    style: Cytoscape.Stylesheet[];
    elements: cytoscape.ElementDefinition[];
    rankDir: string;
    graphRef: MutableRefObject<GraphMutation | undefined>;
};
export default function Graph(props: Props): JSX.Element;
export {};
