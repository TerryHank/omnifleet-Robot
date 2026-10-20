declare const process: {
    nextTick: (fn: Function, ...args: unknown[]) => void;
    title: string;
    browser: boolean;
    env: {};
    argv: never[];
};
export default process;
