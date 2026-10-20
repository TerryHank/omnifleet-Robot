/**
 * A version of React.useCallback() displaying any errors thrown from the function as toast notifications.
 */
export default function useCallbackWithToast<Args extends unknown[]>(callback: (...args: Args) => Promise<void> | void, deps: unknown[]): (...args: Args) => Promise<void>;
