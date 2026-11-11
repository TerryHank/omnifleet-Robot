/// <reference types="react" />
export declare const MAX_SUPPORTED_LAYOUT_VERSION = 1;
/**
 * Concrete implementation of CurrentLayoutContext.Provider which handles
 * automatically restoring the current layout from LayoutStorage.
 */
export default function CurrentLayoutProvider({ children }: React.PropsWithChildren): JSX.Element;
