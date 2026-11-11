// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
/**
 * Overrides the process method of StateProcessor to be a passthrough.
 *
 * Useful if there is no processing to perform.
 */
export class NoopStateProcessor {
    process(playerState) {
        return playerState;
    }
    aliasSubscriptions(subs) {
        return subs;
    }
}
