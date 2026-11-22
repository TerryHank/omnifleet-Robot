export type Operator = "=" | "<" | "<=" | ">" | ">=";
export type Rule = {
    rawValue: string;
    operator: Operator;
    color: string;
    label: string;
};
export type Config = {
    path: string;
    style: "bulb" | "background";
    rules: Rule[];
    fallbackColor: string;
    fallbackLabel: string;
};
