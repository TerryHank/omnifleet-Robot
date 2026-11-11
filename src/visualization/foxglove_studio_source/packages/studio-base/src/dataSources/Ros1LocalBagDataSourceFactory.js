// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { IterablePlayer, WorkerIterableSource } from "@foxglove/studio-base/players/IterablePlayer";
class Ros1LocalBagDataSourceFactory {
    id = "ros1-local-bagfile";
    type = "file";
    displayName = "ROS 1 Bag";
    iconName = "OpenFile";
    supportedFileTypes = [".bag"];
    initialize(args) {
        const file = args.file;
        if (!file) {
            return;
        }
        const source = new WorkerIterableSource({
            initWorker: () => {
                return new Worker(
                // foxglove-depcheck-used: babel-plugin-transform-import-meta
                new URL("@foxglove/studio-base/players/IterablePlayer/BagIterableSourceWorker.worker", import.meta.url));
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
export default Ros1LocalBagDataSourceFactory;
