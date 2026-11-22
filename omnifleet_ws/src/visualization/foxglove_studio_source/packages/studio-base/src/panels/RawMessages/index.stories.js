import { jsx as _jsx } from "react/jsx-runtime";
import RawMessages from "@foxglove/studio-base/panels/RawMessages";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import { enumAdvancedFixture, enumFixture, fixture, multipleMessagesFilter, multipleNumberMessagesFixture, topicsToDiffFixture, topicsWithIdsToDiffFixture, withMissingData, } from "./fixture";
import { Constants, NodeState } from "./types";
const noDiffConfig = {
    diffMethod: "custom",
    diffTopicPath: "",
    diffEnabled: false,
    showFullMessageForDiff: false,
};
const diffConfig = {
    topicPath: "/baz/enum_advanced",
    diffMethod: "custom",
    diffTopicPath: "/another/baz/enum_advanced",
    diffEnabled: true,
};
const scrollToBottom = async ({ canvasElement }) => {
    const scrollContainers = canvasElement.querySelectorAll("[data-testid=panel-scroll-container]");
    scrollContainers.forEach((scrollContainer) => {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
    });
};
export default {
    title: "panels/RawMessages",
};
export const Default = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/msgs/big_topic" } }) })),
};
export const Schemaless = {
    render: () => (_jsx(PanelSetup, { fixture: {
            topics: [{ name: "foo", schemaName: undefined }],
            datatypes: new Map(),
            frame: {
                ["foo"]: [
                    {
                        topic: "foo",
                        schemaName: "",
                        message: { bar: 1 },
                        receiveTime: { sec: 0, nsec: 0 },
                        sizeInBytes: 0,
                    },
                ],
            },
        }, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "foo" } }) })),
};
export const Collapsed = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/msgs/big_topic", expansion: "none" } }) })),
};
export const Expanded = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/msgs/big_topic", expansion: "all" } }) })),
};
export const Overridden = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, includeSettings: true, children: _jsx(RawMessages, { overrideConfig: {
                ...noDiffConfig,
                topicPath: "/msgs/big_topic",
                expansion: { LotsOfStuff: NodeState.Collapsed, timestamp_array: NodeState.Expanded },
            } }) })),
};
export const WithReceivetime = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/foo" } }) })),
    name: "With receiveTime",
};
export const DisplayBigValueNum = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/num.value" } }) })),
    name: "Display big value - num",
};
export const DisplayMessageWithBigintValue = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/bigint" } }) })),
};
export const DisplayBigintValue = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/bigint.value" } }) })),
};
export const DisplayBigValueText = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/text.value" } }) })),
    name: "Display big value - text",
};
export const DisplayBigValueTextTruncated = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/text.value_long" } }) })),
    name: "Display big value - text truncated",
    play: scrollToBottom,
};
export const DisplayBigValueTextWithNewlines = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/text.value_with_newlines" } }) })),
    name: "Display big value - text with newlines",
    play: scrollToBottom,
};
export const DisplayBigValueSingleElementArray = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/array.value" } }) })),
    name: "Display big value - single element array",
};
export const DisplaySingleObjectArray = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/array/obj.value" } }) })),
};
export const DisplayBasicEnum = {
    render: () => (_jsx(PanelSetup, { fixture: enumFixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/enum" } }) })),
};
export const DisplayAdvancedEnumUsage = {
    render: () => (_jsx(PanelSetup, { fixture: enumAdvancedFixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/enum_advanced" } }) })),
};
export const WithMissingData = {
    render: () => (_jsx(PanelSetup, { fixture: withMissingData, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/missing_data" } }) })),
};
export const WithATruncatedLongString = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz/text" } }) })),
};
export const DisplayGeometryTypesLength = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/geometry/types" } }) })),
    name: "Display geometry types - length",
};
export const DisplayDiff = {
    render: () => (_jsx(PanelSetup, { fixture: topicsToDiffFixture, children: _jsx(RawMessages, { overrideConfig: { ...diffConfig, expansion: "all", showFullMessageForDiff: false } }) })),
};
export const DisplayFullDiff = {
    render: () => (_jsx(PanelSetup, { fixture: topicsToDiffFixture, children: _jsx(RawMessages, { overrideConfig: { ...diffConfig, expansion: "all", showFullMessageForDiff: true } }) })),
};
export const DisplayDiffWithIDFields = {
    render: () => (_jsx(PanelSetup, { fixture: topicsWithIdsToDiffFixture, children: _jsx(RawMessages, { overrideConfig: {
                ...diffConfig,
                topicPath: "/baz/enum_advanced_array.value",
                diffTopicPath: "/another/baz/enum_advanced_array.value",
                showFullMessageForDiff: false,
                expansion: "all",
            } }) })),
};
export const EmptyDiffMessage = {
    render: () => (_jsx(PanelSetup, { fixture: { topics: [], frame: {} }, children: _jsx(RawMessages, { overrideConfig: { ...diffConfig, showFullMessageForDiff: false } }) })),
};
export const DiffSameMessages = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: {
                topicPath: "/foo",
                diffMethod: "custom",
                diffTopicPath: "/foo",
                diffEnabled: true,
                showFullMessageForDiff: false,
                fontSize: undefined,
            } }) })),
};
export const DiffConsecutiveMessages = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: {
                topicPath: "/foo",
                diffMethod: Constants.PREV_MSG_METHOD,
                diffTopicPath: "",
                diffEnabled: true,
                showFullMessageForDiff: true,
                expansion: "all",
                fontSize: undefined,
            } }) })),
};
export const DiffConsecutiveMessagesWithFilter = {
    render: () => (_jsx(PanelSetup, { fixture: multipleMessagesFilter, children: _jsx(RawMessages, { overrideConfig: {
                topicPath: "/foo{type==2}",
                diffMethod: Constants.PREV_MSG_METHOD,
                diffTopicPath: "",
                diffEnabled: true,
                showFullMessageForDiff: true,
                expansion: "all",
                fontSize: undefined,
            } }) })),
};
export const DiffConsecutiveMessagesWithBigint = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: {
                topicPath: "/baz/bigint",
                diffMethod: Constants.PREV_MSG_METHOD,
                diffTopicPath: "",
                diffEnabled: true,
                showFullMessageForDiff: true,
                expansion: "all",
                fontSize: undefined,
            } }) })),
};
export const DisplayCorrectMessageWhenDiffIsDisabledEvenWithDiffMethodTopicSet = {
    render: () => (_jsx(PanelSetup, { fixture: fixture, children: _jsx(RawMessages, { overrideConfig: {
                topicPath: "/foo",
                diffMethod: Constants.PREV_MSG_METHOD,
                diffTopicPath: "/another/baz/enum_advanced",
                diffEnabled: false,
                showFullMessageForDiff: true,
                expansion: "all",
                fontSize: undefined,
            } }) })),
    name: "Display correct message when diff is disabled, even with diff method & topic set",
};
export const MultipleMessagesWithTopLevelFilter = {
    render: () => (_jsx(PanelSetup, { fixture: multipleNumberMessagesFixture, children: _jsx(RawMessages, { overrideConfig: {
                ...noDiffConfig,
                topicPath: "/multiple_number_messages{value==2}",
            } }) })),
    name: "Multiple messages with top-level filter",
};
export const KeyValueObjects = {
    render: () => {
        const namesFixture = {
            datatypes: new Map(Object.entries({
                baz: {
                    definitions: [
                        { name: "obj", type: "obj", isComplex: true },
                        { name: "kv", type: "kv", isComplex: true },
                        { name: "kv_arr", type: "kv", isArray: true, isComplex: true },
                    ],
                },
                obj: {
                    definitions: [
                        { name: "key", type: "int32" },
                        { name: "field", type: "string" },
                    ],
                },
                kv: {
                    definitions: [
                        { name: "key", type: "string" },
                        { name: "value", type: "string" },
                    ],
                },
            })),
            topics: [{ name: "/baz", schemaName: "baz" }],
            frame: {
                "/baz": [
                    {
                        topic: "/baz",
                        receiveTime: { sec: 123, nsec: 456789012 },
                        message: {
                            obj: { key: 1, field: "foo" },
                            kv: { key: "foo", value: "bar" },
                            kv_arr: [
                                { key: "foo", value: "bar" },
                                { key: "baz", value: "qux" },
                            ],
                        },
                        schemaName: "baz",
                        sizeInBytes: 0,
                    },
                ],
            },
        };
        return (_jsx(PanelSetup, { fixture: namesFixture, children: _jsx(RawMessages, { overrideConfig: { ...noDiffConfig, topicPath: "/baz" } }) }));
    },
    name: "Display key/value objects",
};
