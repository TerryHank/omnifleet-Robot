/// <reference types="react" />
import { PanelsActions, LayoutData } from "@foxglove/studio-base/context/CurrentLayoutContext/actions";
/**
 * An alternative implementation of CurrentLayoutProvider, for use in tests, which performs actions
 * synchronously and doesn't require a LayoutManager.
 */
export default function MockCurrentLayoutProvider({ children, initialState, onAction, }: React.PropsWithChildren<{
    initialState?: Partial<LayoutData>;
    onAction?: (action: PanelsActions) => void;
}>): JSX.Element;
