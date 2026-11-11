import { jsx as _jsx } from "react/jsx-runtime";
import DiagnosticSummary from "@foxglove/studio-base/panels/diagnostics/DiagnosticSummary";
import { getDiagnosticId, LEVELS, } from "@foxglove/studio-base/panels/diagnostics/util";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
export default {
    title: "panels/diagnostics/DiagnosticSummary",
    excludeStories: ["makeDiagnosticMessage"],
};
export function makeDiagnosticMessage(level, name, hardware_id, messages, options) {
    return {
        topic: "/diagnostics",
        receiveTime: { sec: 2, nsec: 0 },
        message: {
            header: { frame_id: "", stamp: options?.stamp ?? { sec: 1, nsec: 500000000 }, seq: 0 },
            status: messages.map((message) => ({
                level,
                name,
                hardware_id,
                message,
                values: options?.values ?? [],
            })),
        },
        schemaName: "diagnostic_msgs/DiagnosticArray",
        sizeInBytes: 0,
    };
}
const fixture = {
    topics: [{ name: "/diagnostics", schemaName: "diagnostic_msgs/DiagnosticArray" }],
    frame: {
        "/diagnostics": [
            makeDiagnosticMessage(LEVELS.OK, "name1", "hardware_id1", ["ok"]),
            makeDiagnosticMessage(42, "name4", "hardware_id4/filter", ["unknown level"]),
            makeDiagnosticMessage(LEVELS.ERROR, "name3", "hardware_id3/filter", ["error"]),
            makeDiagnosticMessage(LEVELS.STALE, "name5", "hardware_id5", ["stale"]),
            makeDiagnosticMessage(LEVELS.WARN, "name2", "hardware_id2/filter", ["warn"]),
        ],
    },
};
export const Empty = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: { ...fixture, frame: {} }, children: _jsx(DiagnosticSummary, {}) }));
    },
};
export const Basic = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticSummary, {}) }));
    },
};
export const WithSettings = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, includeSettings: true, children: _jsx(DiagnosticSummary, {}) }));
    },
};
export const WithPinnedNodes = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticSummary, { overrideConfig: {
                    minLevel: 0,
                    pinnedIds: [
                        getDiagnosticId("hardware_id1", "name1"),
                        getDiagnosticId("hardware_id3/filter", "name3"),
                    ],
                    topicToRender: "/diagnostics",
                    hardwareIdFilter: "",
                } }) }));
    },
};
export const WithPinnedNodesAndFilter = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticSummary, { overrideConfig: {
                    minLevel: 2,
                    pinnedIds: [
                        getDiagnosticId("hardware_id1", "name1"),
                        getDiagnosticId("hardware_id3/filter", "name3"),
                    ],
                    topicToRender: "/diagnostics",
                    hardwareIdFilter: "",
                } }) }));
    },
};
export const WithoutSorting = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticSummary, { overrideConfig: {
                    minLevel: 0,
                    pinnedIds: [],
                    topicToRender: "/diagnostics",
                    hardwareIdFilter: "",
                    sortByLevel: false,
                } }) }));
    },
};
export const FilteredByHardwareId = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticSummary, { overrideConfig: {
                    minLevel: 0,
                    pinnedIds: [],
                    topicToRender: "/diagnostics",
                    hardwareIdFilter: "filter",
                    sortByLevel: false,
                } }) }));
    },
};
export const FilteredByLevel = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticSummary, { overrideConfig: {
                    minLevel: 2,
                    pinnedIds: [],
                    topicToRender: "/diagnostics",
                    hardwareIdFilter: "",
                    sortByLevel: false,
                } }) }));
    },
};
export const FilteredByHardwareIdAndLevel = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticSummary, { overrideConfig: {
                    minLevel: 2,
                    pinnedIds: [],
                    topicToRender: "/diagnostics",
                    hardwareIdFilter: "filter",
                    sortByLevel: false,
                } }) }));
    },
};
export const OldDiagnosticsMarkedStale = {
    render: () => {
        return (_jsx(PanelSetup, { includeSettings: true, fixture: {
                ...fixture,
                activeData: { currentTime: { sec: 10, nsec: 0 } },
                frame: {
                    "/diagnostics": [
                        makeDiagnosticMessage(LEVELS.OK, "name1", "timeout_id", ["2 secs"], {
                            stamp: { sec: 2, nsec: 0 },
                        }),
                        makeDiagnosticMessage(LEVELS.OK, "name2", "timeout_id", ["4 secs"], {
                            stamp: { sec: 4, nsec: 0 },
                        }),
                        makeDiagnosticMessage(LEVELS.OK, "name3", "timeout_id", ["6 secs"], {
                            stamp: { sec: 6, nsec: 0 },
                        }),
                    ],
                },
            }, children: _jsx(DiagnosticSummary, { overrideConfig: {
                    minLevel: 0,
                    pinnedIds: [],
                    topicToRender: "/diagnostics",
                    hardwareIdFilter: "",
                    sortByLevel: false,
                } }) }));
    },
};
