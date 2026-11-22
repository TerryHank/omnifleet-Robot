// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { downloadFiles } from "@foxglove/studio-base/util/download";
import { formatTimeRaw } from "@foxglove/studio-base/util/time";
function getCSVRow(label, data) {
    const { x, receiveTime, headerStamp, value } = data;
    const receiveTimeFloat = formatTimeRaw(receiveTime);
    const stampTime = headerStamp ? formatTimeRaw(headerStamp) : "";
    return [x, receiveTimeFloat, stampTime, label, value];
}
const getCSVColName = (xAxisVal) => {
    switch (xAxisVal) {
        case "custom":
        case "currentCustom":
            return "x value";
        case "index":
            return "index";
        case "timestamp":
            return "elapsed time";
    }
    return "x";
};
function generateCSV(datasets, xAxisVal) {
    const headLine = [getCSVColName(xAxisVal), "receive time", "header.stamp", "topic", "value"];
    const combinedLines = [headLine];
    for (const dataset of datasets) {
        for (const datum of dataset.data) {
            combinedLines.push(getCSVRow(dataset.label, datum));
        }
    }
    return combinedLines.join("\n");
}
function downloadCSV(filename, datasets, xAxisVal) {
    const csvData = generateCSV(datasets, xAxisVal);
    const blob = new Blob([csvData], { type: "text/csv;charset=utf-8;" });
    downloadFiles([{ blob, fileName: `${filename}.csv` }]);
}
export { downloadCSV, generateCSV };
