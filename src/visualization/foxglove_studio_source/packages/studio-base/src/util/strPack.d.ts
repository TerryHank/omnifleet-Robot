/**
 * Deduplicate all string references in the given data structure. This is
 * useful to do after `postMessage()`, since `structuredClone()` duplicates
 * strings.
 *
 * See: https://bugs.chromium.org/p/chromium/issues/detail?id=1487682&q=&can=4
 */
export default function strPack<T>(data: T): T;
