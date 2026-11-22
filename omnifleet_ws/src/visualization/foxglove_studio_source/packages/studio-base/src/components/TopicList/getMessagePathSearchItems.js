// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as _ from "lodash-es";
import { quoteFieldNameIfNeeded, quoteTopicNameIfNeeded } from "@foxglove/message-path";
/**
 * @param prefix Prepended to each item's {@link MessagePathSuffix.pathSuffix}
 * @param seenSchemaNames List of schema names that have been visited, including the current {@link schema}
 */
function* generateMessagePathSuffixesForSchema(schema, schemasByName, prefix, seenSchemaNames) {
    for (const { name, isArray, isConstant, isComplex, type } of schema.definitions) {
        if (isConstant === true) {
            continue;
        }
        const pathSuffix = `${prefix}.${quoteFieldNameIfNeeded(name)}`;
        yield {
            pathSuffix,
            type: isArray === true ? `${type}[]` : type,
            isLeaf: isComplex !== true,
        };
        if (isComplex === true) {
            if (seenSchemaNames.includes(type)) {
                continue;
            }
            const fieldSchema = schemasByName.get(type);
            if (!fieldSchema) {
                continue;
            }
            yield* generateMessagePathSuffixesForSchema(fieldSchema, schemasByName, isArray === true ? `${pathSuffix}[:]` : pathSuffix, [...seenSchemaNames, type]);
        }
    }
}
/**
 * Get the list of all message path search items in the TopicList (entries to be passed to fzf).
 * This includes an entry for each message path nested underneath each topic.
 */
export function getMessagePathSearchItems(allTopics, schemasByName) {
    const items = [];
    const itemsByTopicName = new Map();
    const topicsBySchemaName = _.groupBy(allTopics.filter((topic) => topic.schemaName != undefined), (topic) => topic.schemaName);
    for (const [schemaName, topics] of Object.entries(topicsBySchemaName)) {
        const schema = schemasByName.get(schemaName);
        if (!schema) {
            continue;
        }
        for (const suffix of generateMessagePathSuffixesForSchema(schema, schemasByName, "", [
            schemaName,
        ])) {
            for (const topic of topics) {
                const quotedTopicName = quoteTopicNameIfNeeded(topic.name);
                const item = {
                    topic,
                    suffix,
                    fullPath: quotedTopicName + suffix.pathSuffix,
                    offset: quotedTopicName.length,
                };
                items.push(item);
                let itemsForTopic = itemsByTopicName.get(topic.name);
                if (!itemsForTopic) {
                    itemsForTopic = [];
                    itemsByTopicName.set(topic.name, itemsForTopic);
                }
                itemsForTopic.push(item);
            }
        }
    }
    return { items, itemsByTopicName };
}
