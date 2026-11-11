import { MessageWriter } from "./MessageWriter";
export declare class JsonMessageWriter implements MessageWriter {
    writeMessage(message: unknown): Uint8Array;
}
