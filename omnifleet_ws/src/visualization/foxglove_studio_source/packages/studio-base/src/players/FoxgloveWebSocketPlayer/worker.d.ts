export type ToWorkerMessage = {
    type: "open";
    data: {
        wsUrl: string;
        protocols?: string[] | string;
    };
} | {
    type: "close";
    data: undefined;
} | {
    type: "data";
    data: string | ArrayBuffer | ArrayBufferView;
};
export type FromWorkerMessage = {
    type: "open";
    protocol: string;
} | {
    type: "close";
    data: unknown;
} | {
    type: "error";
    error: unknown;
} | {
    type: "message";
    data: unknown;
};
