// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { IterablePlayer, WorkerIterableSource } from "@foxglove/studio-base/players/IterablePlayer";
class McapLocalDataSourceFactory {
    id = "mcap-local-file";
    type = "file";
    displayName = "MCAP";
    iconName = "OpenFile";
    supportedFileTypes = [".mcap"];
    initialize(args) {
        const file = args.file;
        if (!file) {
            return;
        }
        const source = new WorkerIterableSource({
            initWorker: () => {
                return new Worker(
                // foxglove-depcheck-used: babel-plugin-transform-import-meta
                new URL("@foxglove/studio-base/players/IterablePlayer/Mcap/McapIterableSourceWorker.worker", import.meta.url));
            },
            initArgs: { file },
        });
        return new IterablePlayer({
            metricsCollector: args.metricsCollector,
            source,
            name: file.name,
            sourceId: this.id,
        });
    }
}
export default McapLocalDataSourceFactory;
