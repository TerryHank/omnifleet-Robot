import EventEmitter from "eventemitter3";
export type Path = ReadonlyArray<string>;
export declare class NodeError {
    path: Path;
    errorsById?: Map<string, string>;
    children?: Map<string, NodeError>;
    constructor(path: Path);
    errorMessage(): string | undefined;
    errorAtPath(path: Path): string | undefined;
    clone(): NodeError;
}
export type LayerErrorEvents = {
    update: (path: Path, errorId: string, errorMessage: string) => void;
    remove: (path: Path, errorId: string) => void;
    clear: (path: Path) => void;
};
export declare class LayerErrors extends EventEmitter<LayerErrorEvents> {
    #private;
    errors: NodeError;
    add(path: Path, errorId: string, errorMessage: string): void;
    addToTopic(topicId: string, errorId: string, errorMessage: string): void;
    hasError(path: Path, errorId: string): boolean;
    remove(path: Path, errorId: string): void;
    removeFromTopic(topicId: string, errorId: string): void;
    /**
     * If value is falsy then add error to path, otherwise remove error from settings path
     * @param value - value to check, if false, add error, if true, remove error
     * @param path  - path to add/remove error
     * @param errorId - id unique to error
     * @param errorMessage - error message
     */
    errorIfFalse(value: boolean, path: Path, errorId: string, errorMessage: string): void;
    clearPath(path: Path): void;
    clearTopic(topicId: string): void;
    clear(): void;
}
