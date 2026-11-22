// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import * as _ from "lodash-es";
import { filterMap } from "@foxglove/den/collection";
import { simpleGetMessagePathDataItems } from "@foxglove/studio-base/components/MessagePathSyntax/simpleGetMessagePathDataItems";
import { getChartValue, isChartValue } from "../datum";
import { mathFunctions } from "../mathFunctions";
/**
 * CurrentCustomDatasetsBuilder builds datasets from a custom x-axis message path and
 * y-axis message path. It uses only the latest message for each path to build the datasets.
 */
export class CurrentCustomDatasetsBuilder {
    #xParsedPath;
    #xValues = [];
    #seriesByKey = new Map();
    #pathsWithMismatchedDataLengths = new Set();
    // Process the latest messages from the player state to extract any updated x or y values
    //
    // Datasets are built when y-values arrive though this could be expanded to also build
    // when x-values arrive.
    handlePlayerState(state) {
        const activeData = state.activeData;
        if (!activeData || !this.#xParsedPath) {
            return;
        }
        const msgEvents = activeData.messages;
        if (msgEvents.length === 0) {
            return;
        }
        let datasetsChanged = false;
        {
            const xAxisMathFn = (this.#xParsedPath.modifier ? mathFunctions[this.#xParsedPath.modifier] : undefined) ??
                (_.identity);
            const msgEvent = lastMatchingTopic(msgEvents, this.#xParsedPath.topicName);
            if (msgEvent) {
                const items = simpleGetMessagePathDataItems(msgEvent, this.#xParsedPath);
                datasetsChanged ||= items.length > 0;
                this.#xValues = [];
                for (const item of items) {
                    if (!isChartValue(item)) {
                        continue;
                    }
                    const chartValue = getChartValue(item);
                    if (chartValue == undefined) {
                        continue;
                    }
                    this.#xValues.push(xAxisMathFn(chartValue));
                }
            }
        }
        for (const series of this.#seriesByKey.values()) {
            const mathFn = series.parsed.modifier ? mathFunctions[series.parsed.modifier] : undefined;
            const msgEvent = lastMatchingTopic(msgEvents, series.parsed.topicName);
            if (!msgEvent) {
                continue;
            }
            const items = simpleGetMessagePathDataItems(msgEvent, series.parsed);
            datasetsChanged ||= items.length > 0;
            const pathItems = filterMap(items, (item, idx) => {
                if (!isChartValue(item)) {
                    return;
                }
                const chartValue = getChartValue(item);
                const mathModifiedValue = mathFn && chartValue != undefined ? mathFn(chartValue) : undefined;
                return {
                    x: this.#xValues[idx] ?? NaN,
                    y: chartValue == undefined ? NaN : mathModifiedValue ?? chartValue,
                    receiveTime: msgEvent.receiveTime,
                    value: mathModifiedValue ?? item,
                };
            });
            if (pathItems.length === this.#xValues.length) {
                this.#pathsWithMismatchedDataLengths.delete(series.messagePath);
            }
            else {
                this.#pathsWithMismatchedDataLengths.add(series.messagePath);
            }
            series.dataset.data = pathItems;
        }
        return {
            range: undefined,
            datasetsChanged,
        };
    }
    setXPath(path) {
        if (JSON.stringify(path) === JSON.stringify(this.#xParsedPath)) {
            return;
        }
        // When the x-path changes we clear any existing data from the datasets
        this.#xParsedPath = path;
        for (const series of this.#seriesByKey.values()) {
            series.dataset.data = [];
        }
        this.#pathsWithMismatchedDataLengths.clear();
    }
    setSeries(series) {
        // Make a new map so we drop series which are no longer present
        const newSeries = new Map();
        for (const item of series) {
            let existingSeries = this.#seriesByKey.get(item.key);
            if (!existingSeries) {
                existingSeries = {
                    configIndex: item.configIndex,
                    enabled: item.enabled,
                    messagePath: item.messagePath,
                    parsed: item.parsed,
                    dataset: {
                        data: [],
                    },
                };
            }
            existingSeries.configIndex = item.configIndex;
            existingSeries.enabled = item.enabled;
            existingSeries.dataset = {
                ...existingSeries.dataset,
                borderColor: item.color,
                showLine: item.showLine,
                fill: false,
                borderWidth: item.lineSize,
                pointRadius: item.lineSize * 1.2,
                pointHoverRadius: 3,
                pointBackgroundColor: item.showLine ? item.contrastColor : item.color,
                pointBorderColor: "transparent",
            };
            newSeries.set(item.key, existingSeries);
        }
        this.#seriesByKey = newSeries;
    }
    // We don't use the viewport because we do not do any downsampling on the assumption that
    // one message won't produce so many points that we need to downsample.
    //
    // If that assumption changes then downsampling can be revisited.
    async getViewportDatasets() {
        const datasets = [];
        for (const series of this.#seriesByKey.values()) {
            if (series.enabled) {
                datasets[series.configIndex] = series.dataset;
            }
        }
        return {
            datasetsByConfigIndex: datasets,
            pathsWithMismatchedDataLengths: this.#pathsWithMismatchedDataLengths,
        };
    }
    async getCsvData() {
        const datasets = [];
        for (const series of this.#seriesByKey.values()) {
            if (!series.enabled) {
                continue;
            }
            datasets.push({
                label: series.messagePath,
                data: series.dataset.data,
            });
        }
        return datasets;
    }
}
function lastMatchingTopic(msgEvents, topic) {
    for (let i = msgEvents.length - 1; i >= 0; --i) {
        const msgEvent = msgEvents[i];
        if (msgEvent.topic === topic) {
            return msgEvent;
        }
    }
    return undefined;
}
