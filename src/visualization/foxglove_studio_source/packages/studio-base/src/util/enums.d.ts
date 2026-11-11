export declare const constantsByDatatype: (datatypes: ReadonlyMap<string, {
    readonly name?: string | undefined;
    readonly definitions: readonly {
        readonly type: string;
        readonly name: string;
        readonly isComplex?: boolean | undefined;
        readonly isArray?: boolean | undefined;
        readonly arrayLength?: number | undefined;
        readonly isConstant?: boolean | undefined;
        readonly value?: import("@foxglove/message-definition").ConstantValue;
        readonly valueText?: string | undefined;
        readonly upperBound?: number | undefined;
        readonly arrayUpperBound?: number | undefined;
        readonly defaultValue?: string | number | bigint | boolean | readonly string[] | readonly number[] | readonly boolean[] | readonly bigint[] | undefined;
        readonly optional?: boolean | undefined;
    }[];
}>) => Record<string, Record<string, string>>;
export declare function extractTypeFromStudioEnumAnnotation(name: string): string | undefined;
export declare const enumValuesByDatatypeAndField: (datatypes: ReadonlyMap<string, {
    readonly name?: string | undefined;
    readonly definitions: readonly {
        readonly type: string;
        readonly name: string;
        readonly isComplex?: boolean | undefined;
        readonly isArray?: boolean | undefined;
        readonly arrayLength?: number | undefined;
        readonly isConstant?: boolean | undefined;
        readonly value?: import("@foxglove/message-definition").ConstantValue;
        readonly valueText?: string | undefined;
        readonly upperBound?: number | undefined;
        readonly arrayUpperBound?: number | undefined;
        readonly defaultValue?: string | number | bigint | boolean | readonly string[] | readonly number[] | readonly boolean[] | readonly bigint[] | undefined;
        readonly optional?: boolean | undefined;
    }[];
}>) => {
    [datatype: string]: {
        [field: string]: {
            [value: string]: string;
        };
    };
};
