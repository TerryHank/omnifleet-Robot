// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { ROS2_TO_DEFINITIONS, Rosbag2, SqliteSqljs } from "@foxglove/rosbag2-web";
import { stringify } from "@foxglove/rosmsg";
import { add as addTime } from "@foxglove/rostime";
import { estimateObjectSize } from "@foxglove/studio-base/players/messageMemoryEstimation";
import { basicDatatypes } from "@foxglove/studio-base/util/basicDatatypes";
export class RosDb3IterableSource {
    #files;
    #bag;
    #start = { sec: 0, nsec: 0 };
    #end = { sec: 0, nsec: 0 };
    #messageSizeEstimateByTopic = {};
    constructor(files) {
        this.#files = files;
    }
    async initialize() {
        const res = await fetch(
        // foxglove-depcheck-used: babel-plugin-transform-import-meta
        new URL("@foxglove/sql.js/dist/sql-wasm.wasm", import.meta.url).toString());
        const sqlWasm = await (await res.blob()).arrayBuffer();
        await SqliteSqljs.Initialize({ wasmBinary: sqlWasm });
        const dbs = this.#files.map((file) => new SqliteSqljs(file));
        const bag = new Rosbag2(dbs);
        await bag.open();
        this.#bag = bag;
        const [start, end] = await this.#bag.timeRange();
        const topicDefs = await this.#bag.readTopics();
        const messageCounts = await this.#bag.messageCounts();
        let hasAnyMessages = false;
        for (const count of messageCounts.values()) {
            if (count > 0) {
                hasAnyMessages = true;
                break;
            }
        }
        if (!hasAnyMessages) {
            throw new Error("Bag contains no messages");
        }
        const problems = [];
        const topics = [];
        const topicStats = new Map();
        // ROS 2 .db3 files do not contain message definitions, so we can only support well-known ROS types.
        const datatypes = new Map([...ROS2_TO_DEFINITIONS, ...basicDatatypes]);
        const messageDefinitionsByTopic = {};
        const parsedMessageDefinitionsByTopic = {};
        for (const topicDef of topicDefs) {
            const numMessages = messageCounts.get(topicDef.name);
            topics.push({ name: topicDef.name, schemaName: topicDef.type });
            if (numMessages != undefined) {
                topicStats.set(topicDef.name, { numMessages });
            }
            const parsedMsgdef = datatypes.get(topicDef.type);
            if (parsedMsgdef == undefined) {
                problems.push({
                    severity: "warn",
                    message: `Topic "${topicDef.name}" has unsupported datatype "${topicDef.type}"`,
                    tip: "ROS 2 .db3 files do not contain message definitions, so only well-known ROS types are supported in Foxglove Studio. As a workaround, you can convert the db3 file to mcap using the mcap CLI. For more information, see: https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2",
                });
                continue;
            }
            const fullParsedMessageDefinitions = [parsedMsgdef];
            const messageDefinition = stringify(fullParsedMessageDefinitions);
            datatypes.set(topicDef.type, { name: topicDef.type, definitions: parsedMsgdef.definitions });
            messageDefinitionsByTopic[topicDef.name] = messageDefinition;
            parsedMessageDefinitionsByTopic[topicDef.name] = fullParsedMessageDefinitions;
        }
        this.#start = start;
        this.#end = end;
        return {
            topics: Array.from(topics.values()),
            topicStats,
            start,
            end,
            problems,
            profile: "ros2",
            datatypes,
            publishersByTopic: new Map(),
        };
    }
    async *messageIterator(opt) {
        if (this.#bag == undefined) {
            throw new Error(`Rosbag2DataProvider is not initialized`);
        }
        const topics = opt.topics;
        if (topics.size === 0) {
            return;
        }
        const start = opt.start ?? this.#start;
        const end = opt.end ?? this.#end;
        // Add 1 nsec to the end time because rosbag2 treats the time range as non-inclusive
        // of the exact end time.
        const inclusiveEndTime = addTime(end, { sec: 0, nsec: 1 });
        const msgIterator = this.#bag.readMessages({
            startTime: start,
            endTime: inclusiveEndTime,
            topics: Array.from(topics.keys()),
        });
        for await (const msg of msgIterator) {
            // Lookup the size estimate for this topic or compute it if not found in the cache.
            let msgSizeEstimate = this.#messageSizeEstimateByTopic[msg.topic.name];
            if (msgSizeEstimate == undefined) {
                msgSizeEstimate = estimateObjectSize(msg.value);
                this.#messageSizeEstimateByTopic[msg.topic.name] = msgSizeEstimate;
            }
            yield {
                type: "message-event",
                msgEvent: {
                    topic: msg.topic.name,
                    receiveTime: msg.timestamp,
                    message: msg.value,
                    sizeInBytes: Math.max(msg.data.byteLength, msgSizeEstimate),
                    schemaName: msg.topic.type,
                },
            };
        }
    }
    async getBackfillMessages(_args) {
        return [];
    }
}
