import type { OsContext } from "@foxglove/studio-base/OsContext";
/** Global singleton of the OsContext provided by the bridge */
declare const OsContextSingleton: OsContext | undefined;
export default OsContextSingleton;
