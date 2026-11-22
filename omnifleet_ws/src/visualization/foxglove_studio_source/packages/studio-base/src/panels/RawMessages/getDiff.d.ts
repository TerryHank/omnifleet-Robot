/// <reference types="lodash" />
export declare const diffArrow = "->";
export declare const diffLabels: {
    readonly ADDED: {
        readonly labelText: "STUDIO_DIFF___ADDED";
        readonly color: "#404047";
        readonly backgroundColor: "#daffe7";
        readonly invertedBackgroundColor: "#182924";
        readonly indicator: "+";
    };
    readonly DELETED: {
        readonly labelText: "STUDIO_DIFF___DELETED";
        readonly color: "#404047";
        readonly backgroundColor: "#ffdee3";
        readonly invertedBackgroundColor: "#3d2327";
        readonly indicator: "-";
    };
    readonly CHANGED: {
        readonly labelText: "STUDIO_DIFF___CHANGED";
        readonly color: "#eba800";
    };
    readonly ID: {
        readonly labelText: "STUDIO_DIFF___ID";
    };
};
export declare const diffLabelsByLabelText: import("lodash").Dictionary<{
    readonly labelText: "STUDIO_DIFF___ADDED";
    readonly color: "#404047";
    readonly backgroundColor: "#daffe7";
    readonly invertedBackgroundColor: "#182924";
    readonly indicator: "+";
} | {
    readonly labelText: "STUDIO_DIFF___DELETED";
    readonly color: "#404047";
    readonly backgroundColor: "#ffdee3";
    readonly invertedBackgroundColor: "#3d2327";
    readonly indicator: "-";
} | {
    readonly labelText: "STUDIO_DIFF___CHANGED";
    readonly color: "#eba800";
} | {
    readonly labelText: "STUDIO_DIFF___ID";
}>;
export type DiffObject = Record<string, unknown>;
export default function getDiff({ before, after, idLabel, showFullMessageForDiff, }: {
    before: unknown;
    after: unknown;
    idLabel?: string;
    showFullMessageForDiff?: boolean;
}): undefined | DiffObject | DiffObject[];
