import { Fragment as _Fragment, jsx as _jsx } from "react/jsx-runtime";
/**
 * Reduces the amount of nesting required to wrap a subtree with multiple React context providers.
 * Rather than indenting each provider inside the next, all providers can be passed in a flat array
 * to the MultiProvider.
 */
export default function MultiProvider({ children, providers, }) {
    const wrapped = providers.reduceRight((wrappedChildren, provider) => React.cloneElement(provider, undefined, wrappedChildren), children);
    // TS requires our return type to be Element instead of Node
    return _jsx(_Fragment, { children: wrapped });
}
