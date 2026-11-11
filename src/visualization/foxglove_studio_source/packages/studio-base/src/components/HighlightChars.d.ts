/// <reference types="react" />
type Props = {
    str: string;
    indices: Set<number>;
    offset?: number;
};
/**
 * Renders the given text with the characters highlighted text wrapped in a
 * <mark> component for Fzf results. The indices are the positions of the
 * matched characters in the original string.
 *
 * Optionally, an offset can be provided to account for the fact that the search
 * string may be a substring of the original string.
 */
export declare function HighlightChars(props: Props): JSX.Element;
export {};
