export interface MessageWriter {
    writeMessage(message: unknown): Uint8Array;
}
