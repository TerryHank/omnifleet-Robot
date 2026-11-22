// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
export function makeMockAppConfiguration(entries) {
    const map = new Map(entries);
    const listeners = new Map();
    return {
        get: (key) => map.get(key),
        set: async (key, value) => {
            map.set(key, value);
            [...(listeners.get(key) ?? [])].forEach((listener) => {
                listener(value);
            });
        },
        addChangeListener: (key, cb) => {
            let listenersForKey = listeners.get(key);
            if (!listenersForKey) {
                listenersForKey = new Set();
                listeners.set(key, listenersForKey);
            }
            listenersForKey.add(cb);
        },
        removeChangeListener: (key, cb) => listeners.get(key)?.delete(cb),
    };
}
