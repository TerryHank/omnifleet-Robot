import { IWebSocket } from "@foxglove/ws-protocol";
export default class WorkerSocketAdapter implements IWebSocket {
    #private;
    binaryType: string;
    protocol: string;
    onerror: ((event: unknown) => void) | undefined;
    onopen: ((event: unknown) => void) | undefined;
    onclose: ((event: unknown) => void) | undefined;
    onmessage: ((event: unknown) => void) | undefined;
    constructor(wsUrl: string, protocols?: string[] | string);
    close(): void;
    send(data: string | ArrayBuffer | ArrayBufferView): void;
}
