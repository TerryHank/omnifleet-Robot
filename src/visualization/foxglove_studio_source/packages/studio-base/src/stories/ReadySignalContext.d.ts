/// <reference types="react" />
export type ReadySignal = () => void;
declare const ReadySignalContext: import("react").Context<ReadySignal | undefined>;
/**
 * useReadySignal returns a function that can be called to indicate a story is ready to be captured
 * for a screenshot test. To use this, the story must have the `useReadySignal` parameter set, i.e.
 * `Story.parameters = { useReadySignal: true }`.
 *
 * An optional `count` can be set to require multiple calls to the returned function before the
 * story will be marked as ready.
 */
declare function useReadySignal({ count }?: {
    count: number;
}): ReadySignal;
export { useReadySignal };
export default ReadySignalContext;
