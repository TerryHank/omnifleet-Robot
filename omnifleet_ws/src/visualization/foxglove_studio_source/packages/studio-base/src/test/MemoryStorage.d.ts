export default class MemoryStorage {
    #private;
    [key: string]: unknown;
    constructor(quota?: number);
    clear(): void;
    getItem(key: string): string | undefined;
    setItem(key: string, value: string): void;
    removeItem(key: string): void;
}
