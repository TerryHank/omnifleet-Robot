import { LogMessageEvent } from "./types";
export default function filterMessages(events: readonly LogMessageEvent[], filter: {
    minLogLevel: number;
    searchTerms: string[];
    nameFilter: Record<string, {
        visible?: boolean;
    }>;
}): readonly LogMessageEvent[];
