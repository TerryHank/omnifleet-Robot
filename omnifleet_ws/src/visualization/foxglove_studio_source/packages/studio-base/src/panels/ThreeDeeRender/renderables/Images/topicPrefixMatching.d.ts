/**
 * Get a prefix of the given `topic` which can be used to match against related image, calibration, or annotation topics.
 *
 * Matches everything up to the last `/` in a topic name, e.g. `getTopicMatchPrefix("/a/b/c")` returns `"/a/b/"`.
 */
export declare function getTopicMatchPrefix(topic: string): string | undefined;
/**
 * Sort the given `array` so items for which `key(item)` matches the prefix of the given `imageTopic` are at the beginning.
 */
export declare function sortPrefixMatchesToFront<T>(array: T[], imageTopic: string, key: (item: T) => string): void;
