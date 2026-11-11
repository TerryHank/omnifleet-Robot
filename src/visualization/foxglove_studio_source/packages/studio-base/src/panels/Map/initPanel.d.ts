import { useCrash } from "@foxglove/hooks";
import { PanelExtensionContext } from "@foxglove/studio";
import "leaflet/dist/leaflet.css";
export declare function initPanel(crash: ReturnType<typeof useCrash>, context: PanelExtensionContext): () => void;
