import type { VariableValue } from "@foxglove/studio";
export type GlobalVariables = {
    [key: string]: VariableValue;
};
export declare const EMPTY_GLOBAL_VARIABLES: GlobalVariables;
export default function useGlobalVariables(): {
    globalVariables: GlobalVariables;
    setGlobalVariables: (arg0: GlobalVariables) => void;
    overwriteGlobalVariables: (arg0: GlobalVariables) => void;
};
