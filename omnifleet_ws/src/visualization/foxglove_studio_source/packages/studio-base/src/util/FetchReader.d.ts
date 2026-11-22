import { EventEmitter } from "eventemitter3";
type EventTypes = {
    data: (chunk: Uint8Array) => void;
    end: () => void;
    error: (err: Error) => void;
};
export default class FetchReader extends EventEmitter<EventTypes> {
    #private;
    constructor(url: string, options?: RequestInit);
    read(): void;
    destroy(): void;
}
export {};
