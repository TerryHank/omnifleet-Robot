import { PropsWithChildren } from "react";
/**
 * Reduces the amount of nesting required to wrap a subtree with multiple React context providers.
 * Rather than indenting each provider inside the next, all providers can be passed in a flat array
 * to the MultiProvider.
 */
export default function MultiProvider({ children, providers, }: PropsWithChildren<{
    providers: readonly JSX.Element[];
}>): JSX.Element;
