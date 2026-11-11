type InitArgs = {
    canvas: OffscreenCanvas;
    devicePixelRatio: number;
    gridColor: string;
    tickColor: string;
};
export type Service<T> = {
    init(args: InitArgs): Promise<T>;
};
export {};
