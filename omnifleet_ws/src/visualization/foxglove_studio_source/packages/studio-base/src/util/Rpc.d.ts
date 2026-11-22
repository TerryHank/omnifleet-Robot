export interface Channel {
    postMessage(data: unknown, transfer?: Transferable[]): void;
    onmessage?: ((ev: MessageEvent) => unknown) | null;
    terminate: () => void;
}
export declare function createLinkedChannels(): {
    local: Channel;
    remote: Channel;
};
export default class Rpc {
    #private;
    static transferables: string;
    constructor(channel: Omit<Channel, "terminate">);
    /** Call this when the channel has been terminated to reject any outstanding send callbacks. */
    terminate(): void;
    send<TResult, TData = unknown>(topic: string, data?: TData, transfer?: Transferable[]): Promise<TResult>;
    receive<T, TOut>(topic: string, handler: (arg0: T) => TOut): void;
}
