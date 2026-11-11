import { Immutable } from "@foxglove/studio";
import { SharedPanelState } from "@foxglove/studio-base/context/CurrentLayoutContext";
/**
 * Returns a [state, setState] pair that can be used to read and update shared transient
 * panel state.
 */
export declare function useSharedPanelState(): [
    Immutable<SharedPanelState>,
    (data: Immutable<SharedPanelState>) => void
];
