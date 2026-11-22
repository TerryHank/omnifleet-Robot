import { Rule } from "./types";
export declare function getMatchingRule(rawValue: undefined | boolean | bigint | number | string | {
    data?: boolean | bigint | number | string;
}, rules: readonly Rule[]): Rule | undefined;
