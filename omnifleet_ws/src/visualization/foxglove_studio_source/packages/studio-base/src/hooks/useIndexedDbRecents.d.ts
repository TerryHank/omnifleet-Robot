type RecentRecordCommon = {
    id: string;
    sourceId: string;
    title: string;
    label?: string;
};
type RecentConnectionRecord = RecentRecordCommon & {
    type: "connection";
    extra?: Record<string, string | undefined>;
};
type RecentFileRecord = RecentRecordCommon & {
    type: "file";
    handle: FileSystemFileHandle;
};
type UnsavedRecentRecord = Omit<RecentConnectionRecord, "id"> | Omit<RecentFileRecord, "id">;
export type RecentRecord = RecentConnectionRecord | RecentFileRecord;
interface IRecentsStore {
    recents: RecentRecord[];
    addRecent: (newRecent: UnsavedRecentRecord) => void;
    save: () => Promise<void>;
}
declare function useIndexedDbRecents(): IRecentsStore;
export default useIndexedDbRecents;
