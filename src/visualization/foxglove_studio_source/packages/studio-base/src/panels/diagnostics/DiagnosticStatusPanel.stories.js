import { jsx as _jsx } from "react/jsx-runtime";
import DiagnosticStatusPanel from "@foxglove/studio-base/panels/diagnostics/DiagnosticStatusPanel";
import { makeDiagnosticMessage } from "@foxglove/studio-base/panels/diagnostics/DiagnosticSummary.stories";
import { LEVELS } from "@foxglove/studio-base/panels/diagnostics/util";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
export default {
    title: "panels/diagnostics/DiagnosticStatusPanel",
};
const fixture = {
    topics: [{ name: "/diagnostics", schemaName: "diagnostic_msgs/DiagnosticArray" }],
    frame: {
        "/diagnostics": [
            makeDiagnosticMessage(LEVELS.OK, "name1", "hardware_id1", ["message 1", "message 2"]),
            makeDiagnosticMessage(LEVELS.OK, "name2", "hardware_id1", ["message 3"], {
                values: [
                    { key: "key", value: "value" },
                    { key: "key <b>with html</b>", value: "value <tt>with html</tt>" },
                ],
            }),
            makeDiagnosticMessage(LEVELS.ERROR, "name1", "levels_id", ["error message"]),
            makeDiagnosticMessage(LEVELS.OK, "name2", "levels_id", ["ok message"]),
            makeDiagnosticMessage(LEVELS.STALE, "name3", "levels_id", ["stale message"]),
            makeDiagnosticMessage(LEVELS.WARN, "name4", "levels_id", ["warn message"]),
        ],
    },
};
export const Empty = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticStatusPanel, {}) }));
    },
};
export const Default = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticStatusPanel, { overrideConfig: {
                    topicToRender: "/diagnostics",
                    selectedHardwareId: "levels_id",
                } }) }));
    },
};
export const WithSettings = {
    render: function Story() {
        return (_jsx(PanelSetup, { fixture: fixture, includeSettings: true, children: _jsx(DiagnosticStatusPanel, { overrideConfig: {
                    topicToRender: "/diagnostics",
                    selectedHardwareId: "hardware_id1",
                    selectedName: "name2",
                } }) }));
    },
    parameters: {
        colorScheme: "light",
    },
};
export const SelectedHardwareIDOnly = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticStatusPanel, { overrideConfig: {
                    topicToRender: "/diagnostics",
                    selectedHardwareId: "hardware_id1",
                    selectedName: undefined,
                } }) }));
    },
};
export const SelectedName = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticStatusPanel, { overrideConfig: {
                    topicToRender: "/diagnostics",
                    selectedHardwareId: "hardware_id1",
                    selectedName: "name2",
                } }) }));
    },
};
export const MovedDivider = {
    render: () => {
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(DiagnosticStatusPanel, { overrideConfig: {
                    topicToRender: "/diagnostics",
                    selectedHardwareId: "hardware_id1",
                    selectedName: undefined,
                    splitFraction: 0.25,
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
            }, children: _jsx(DiagnosticStatusPanel, { overrideConfig: {
                    topicToRender: "/diagnostics",
                    selectedHardwareId: "timeout_id",
                    selectedName: undefined,
                } }) }));
    },
};
