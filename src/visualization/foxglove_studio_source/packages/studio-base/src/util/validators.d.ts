export type ValidationResult = string | {
    [fieldName: string]: string;
};
export declare const validationErrorToString: (validationResult: ValidationResult) => string;
