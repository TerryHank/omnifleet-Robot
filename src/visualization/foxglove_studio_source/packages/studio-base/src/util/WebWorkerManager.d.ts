import Rpc, { Channel } from "@foxglove/studio-base/util/Rpc";
type WorkerListenerState<W> = {
    rpc: Rpc;
    worker: W;
    listenerIds: string[];
};
export default class WebWorkerManager<W extends Channel> {
    #private;
    constructor(createWorker: () => W, maxWorkerCount: number);
    testing_workerCount(): number;
    testing_getWorkerState(id: string): WorkerListenerState<W> | undefined;
    registerWorkerListener(id: string): Rpc;
    unregisterWorkerListener(id: string): void;
}
export {};
