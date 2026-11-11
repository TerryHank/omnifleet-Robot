import { PropsWithChildren } from "react";
/**
 * RemountOnValueChange will unmount and remount the children when _value_ changes.
 * This is used when you want to "reset" the component tree for a specific value change.
 *
 * Note: Use sparingly and prefer hook dependencies to manage state updates. This should be a
 * last resort nuclear option when you think that an entire subtree should be purged.
 */
export default function RemountOnValueChange(props: PropsWithChildren<{
    value: unknown;
}>): JSX.Element;
