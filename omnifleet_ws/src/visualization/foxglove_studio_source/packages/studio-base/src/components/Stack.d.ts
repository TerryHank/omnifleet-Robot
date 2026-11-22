import { CSSProperties } from "react";
declare const _default: import("react").ForwardRefExoticComponent<StackProps & {
    children?: import("react").ReactNode;
} & import("react").RefAttributes<HTMLDivElement>>;
export default _default;
export type StackProps = {
    /** Class name applied to the root element. */
    className?: string;
    /**
     * Defines the `flex-direction` style property.
     * @default 'column'
     */
    direction?: CSSProperties["flexDirection"];
    /** Make stack 100% height. */
    fullHeight?: boolean;
    /** Make stack 100% height. */
    fullWidth?: boolean;
    /** Sets the display to inline-flex property. */
    inline?: boolean;
    /** Defines the `justify-content` style property. */
    justifyContent?: CSSProperties["justifyContent"];
    /** Defines the `align-items` style property. */
    alignItems?: CSSProperties["alignItems"];
    /** Defines the `align-content` style property. */
    alignContent?: CSSProperties["alignContent"];
    /** Defines the `align-self` style property. */
    alignSelf?: CSSProperties["alignSelf"];
    /** Defines the `gap` style property using `theme.spacing` increments. */
    gap?: number;
    /** Defines the `rowGap` style property using `theme.spacing` increments. */
    gapX?: number;
    /** Defines the `columnGap` style property using `theme.spacing` increments. */
    gapY?: number;
    /** Defines the `overflow` style property. */
    overflow?: CSSProperties["overflow"];
    /** Defines the `overflow-x` style property. */
    overflowX?: CSSProperties["overflowX"];
    /** Defines the `overflow-y` style property. */
    overflowY?: CSSProperties["overflowY"];
    /** Defines the `padding` style property using `theme.spacing` increments. */
    padding?: number;
    /**
     * Defines the `padding-left` and `padding-right` style property using `theme.spacing` increments. */
    paddingX?: number;
    /** Defines the padding-top` and `padding-bottom` style property using `theme.spacing` increments. */
    paddingY?: number;
    /** Defines the vertical `padding-top` style property using `theme.spacing` increments. */
    paddingTop?: number;
    /** Defines the vertical `padding-bottom` style property using `theme.spacing` increments. */
    paddingBottom?: number;
    /** Defines the vertical `padding-left` style property using `theme.spacing` increments. */
    paddingLeft?: number;
    /** Defines the vertical `padding-right` style property using `theme.spacing` increments. */
    paddingRight?: number;
    /** Defines the vertical `padding-block` style property using `theme.spacing` increments. */
    paddingBlock?: number;
    /** Defines the vertical `padding-block-start` style property using `theme.spacing` increments. */
    paddingBlockStart?: number;
    /** Defines the vertical `padding-block-end` style property using `theme.spacing` increments. */
    paddingBlockEnd?: number;
    /** Defines the vertical `padding-inline` style property using `theme.spacing` increments. */
    paddingInline?: number;
    /** Defines the vertical `padding-inline-start` style property using `theme.spacing` increments. */
    paddingInlineStart?: number;
    /** Defines the vertical `padding-inline-end` style property using `theme.spacing` increments. */
    paddingInlineEnd?: number;
    /** Defines the `position` style property. */
    position?: CSSProperties["position"];
    /** Defines the `flex` style property. */
    flex?: CSSProperties["flex"];
    /** Defines the `flex-grow` style property. */
    flexGrow?: CSSProperties["flexGrow"];
    /** Defines the `flex-shrink` style property. */
    flexShrink?: CSSProperties["flexShrink"];
    /** Defines the `flex-basis` style property. */
    flexBasis?: CSSProperties["flexBasis"];
    /** Defines the `flex-wrap` style property. */
    flexWrap?: CSSProperties["flexWrap"];
    /** Defines the `order` property. */
    order?: CSSProperties["order"];
    /** Sets the minWidth to zero */
    zeroMinWidth?: boolean;
    /** CSS styles to apply to the component. */
    style?: CSSProperties;
    /** HTML title attribute */
    title?: string;
    /** Standard pointer events. */
    onPointerDown?: React.DOMAttributes<HTMLDivElement>["onPointerDown"];
    onPointerEnter?: React.DOMAttributes<HTMLDivElement>["onPointerEnter"];
    onPointerLeave?: React.DOMAttributes<HTMLDivElement>["onPointerLeave"];
    onPointerMove?: React.DOMAttributes<HTMLDivElement>["onPointerMove"];
    onPointerOver?: React.DOMAttributes<HTMLDivElement>["onPointerOver"];
    onPointerUp?: React.DOMAttributes<HTMLDivElement>["onPointerUp"];
};
