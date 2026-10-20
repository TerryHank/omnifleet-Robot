/// <reference types="react" />
import { MosaicPath } from "react-mosaic-component";
/**
 * Exposes the mosaic path at which a panel is located. Unlike calling
 * `mosaicWindowActions.getPath()` during render, subscribing to this context will trigger a
 * re-render when the path changes.
 */
export declare const MosaicPathContext: import("react").Context<MosaicPath | undefined>;
