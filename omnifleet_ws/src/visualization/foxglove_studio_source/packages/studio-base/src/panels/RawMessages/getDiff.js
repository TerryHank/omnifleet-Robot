// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
//
// This file incorporates work covered by the following copyright and
// permission notice:
//
//   Copyright 2019-2021 Cruise LLC
//
//   This source code is licensed under the Apache License, Version 2.0,
//   found at http://www.apache.org/licenses/LICENSE-2.0
//   You may not use this file except in compliance with the License.
import * as _ from "lodash-es";
import { isTypicalFilterName } from "@foxglove/studio-base/components/MessagePathSyntax/isTypicalFilterName";
export const diffArrow = "->";
export const diffLabels = {
    ADDED: {
        labelText: "STUDIO_DIFF___ADDED",
        color: "#404047",
        backgroundColor: "#daffe7",
        invertedBackgroundColor: "#182924",
        indicator: "+",
    },
    DELETED: {
        labelText: "STUDIO_DIFF___DELETED",
        color: "#404047",
        backgroundColor: "#ffdee3",
        invertedBackgroundColor: "#3d2327",
        indicator: "-",
    },
    CHANGED: {
        labelText: "STUDIO_DIFF___CHANGED",
        color: "#eba800",
    },
    ID: { labelText: "STUDIO_DIFF___ID" },
};
export const diffLabelsByLabelText = _.keyBy(Object.values(diffLabels), "labelText");
export default function getDiff({ before, after, idLabel, showFullMessageForDiff = false, }) {
    if (Array.isArray(before) && Array.isArray(after)) {
        let idToCompareWith;
        const allItems = before.concat(after);
        if (typeof allItems[0] === "object" && allItems[0] != undefined) {
            let candidateIdsToCompareWith = {};
            if (allItems[0].id != undefined) {
                candidateIdsToCompareWith.id = { before: [], after: [] };
            }
            for (const key in allItems[0]) {
                if (isTypicalFilterName(key)) {
                    candidateIdsToCompareWith[key] = { before: [], after: [] };
                }
            }
            if (!_.every(allItems, (item) => typeof item === "object" && item)) {
                candidateIdsToCompareWith = {};
            }
            for (const [idKey, candidates] of Object.entries(candidateIdsToCompareWith)) {
                for (const beforeItem of before) {
                    if (beforeItem[idKey] != undefined) {
                        candidates.before.push(beforeItem[idKey]);
                    }
                }
            }
            for (const [idKey, candidates] of Object.entries(candidateIdsToCompareWith)) {
                for (const afterItem of after) {
                    if (afterItem[idKey] != undefined) {
                        candidates.after.push(afterItem[idKey]);
                    }
                }
            }
            for (const [idKey, { before: candidateIdBefore, after: candidateIdAfter }] of Object.entries(candidateIdsToCompareWith)) {
                if (_.uniq(candidateIdBefore).length === before.length &&
                    _.uniq(candidateIdAfter).length === after.length) {
                    idToCompareWith = idKey;
                    break;
                }
            }
        }
        if (idToCompareWith != undefined) {
            const unmatchedAfterById = _.keyBy(after, idToCompareWith);
            const diff = [];
            for (const beforeItem of before) {
                if (beforeItem == undefined || typeof beforeItem !== "object") {
                    throw new Error("beforeItem is invalid; should have checked this earlier");
                }
                const id = beforeItem[idToCompareWith];
                const innerDiff = getDiff({
                    before: beforeItem,
                    after: unmatchedAfterById[id],
                    idLabel: idToCompareWith,
                    showFullMessageForDiff,
                });
                delete unmatchedAfterById[id];
                if (!_.isEmpty(innerDiff)) {
                    const isDeleted = Object.keys(innerDiff).length === 1 &&
                        Object.keys(innerDiff)[0] === diffLabels.DELETED.labelText;
                    diff.push(isDeleted
                        ? innerDiff
                        : {
                            [diffLabels.ID.labelText]: { [idToCompareWith]: id },
                            ...innerDiff,
                        });
                }
            }
            for (const afterItem of Object.values(unmatchedAfterById)) {
                const innerDiff = getDiff({
                    before: undefined,
                    after: afterItem,
                    idLabel: idToCompareWith,
                    showFullMessageForDiff,
                });
                if (!_.isEmpty(innerDiff)) {
                    diff.push(innerDiff);
                }
            }
            return diff;
        }
    }
    if (typeof before === "object" && typeof after === "object" && before && after) {
        const diff = {};
        const allKeys = Object.keys(before).concat(Object.keys(after));
        for (const key of _.uniq(allKeys)) {
            const innerDiff = getDiff({
                before: before[key],
                after: after[key],
                idLabel: undefined,
                showFullMessageForDiff,
            });
            if (!_.isEmpty(innerDiff)) {
                diff[key] = innerDiff;
            }
            else if (showFullMessageForDiff) {
                diff[key] = before[key];
            }
        }
        return diff;
    }
    if (before === after) {
        return undefined;
    }
    if (before == undefined) {
        const afterIsNotObj = Array.isArray(after) || typeof after !== "object";
        if (!idLabel || afterIsNotObj) {
            return { [diffLabels.ADDED.labelText]: after };
        }
        const idLabelObj = {
            [diffLabels.ID.labelText]: { [idLabel]: { ...after }[idLabel] },
        };
        return {
            [diffLabels.ADDED.labelText]: { ...idLabelObj, ...after },
        };
    }
    if (after == undefined) {
        const beforeIsNotObj = Array.isArray(before) || typeof before !== "object";
        if (!idLabel || beforeIsNotObj) {
            return { [diffLabels.DELETED.labelText]: before };
        }
        const idLabelObj = {
            [diffLabels.ID.labelText]: { [idLabel]: { ...before }[idLabel] },
        };
        return {
            [diffLabels.DELETED.labelText]: { ...idLabelObj, ...before },
        };
    }
    const beforeText = typeof before === "bigint" ? before.toString() : JSON.stringify(before);
    const afterText = typeof after === "bigint" ? after.toString() : JSON.stringify(after);
    return {
        [diffLabels.CHANGED.labelText]: `${beforeText} ${diffArrow} ${afterText}`,
    };
}
