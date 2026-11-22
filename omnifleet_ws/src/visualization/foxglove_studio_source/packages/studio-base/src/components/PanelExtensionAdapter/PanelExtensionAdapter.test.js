import { jsx as _jsx } from "react/jsx-runtime";
/** @jest-environment jsdom */
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
/* eslint-disable jest/no-done-callback */
import { render } from "@testing-library/react";
import { act } from "react-dom/test-utils";
import { Condvar, signal } from "@foxglove/den/async";
import MockPanelContextProvider from "@foxglove/studio-base/components/MockPanelContextProvider";
import { PlayerCapabilities } from "@foxglove/studio-base/players/types";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import ThemeProvider from "@foxglove/studio-base/theme/ThemeProvider";
import PanelExtensionAdapter from "./PanelExtensionAdapter";
describe("PanelExtensionAdapter", () => {
    it("should call initPanel", async () => {
        expect.assertions(1);
        const sig = signal();
        const initPanel = (context) => {
            expect(context).toBeDefined();
            sig.resolve();
        };
        const config = {};
        const saveConfig = () => { };
        const Wrapper = () => {
            return (_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { children: _jsx(PanelExtensionAdapter, { config: config, saveConfig: saveConfig, initPanel: initPanel }) }) }) }));
        };
        const handle = render(_jsx(Wrapper, {}));
        await act(async () => undefined);
        // force a re-render to make sure we do not call init panel again
        handle.rerender(_jsx(Wrapper, {}));
        await sig;
    });
    it("sets didSeek=true when seeking", async () => {
        const mockRAF = jest
            .spyOn(window, "requestAnimationFrame")
            // eslint-disable-next-line @typescript-eslint/no-confusing-void-expression
            .mockImplementation((cb) => queueMicrotask(() => cb(performance.now())));
        const renderStates = [];
        const initPanel = jest.fn((context) => {
            context.watch("currentFrame");
            context.watch("didSeek");
            context.subscribe(["x"]);
            context.onRender = (renderState, done) => {
                renderStates.push({ ...renderState });
                done();
            };
        });
        const config = {};
        const saveConfig = () => { };
        const message = {
            topic: "x",
            receiveTime: { sec: 0, nsec: 1 },
            sizeInBytes: 0,
            message: 42,
            schemaName: "foo",
        };
        const Wrapper = ({ lastSeekTime }) => {
            return (_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: {
                            activeData: { lastSeekTime },
                            frame: {
                                x: [message],
                            },
                        }, children: _jsx(PanelExtensionAdapter, { config: config, saveConfig: saveConfig, initPanel: initPanel }) }) }) }));
        };
        const wrapper = render(_jsx(Wrapper, { lastSeekTime: undefined }));
        expect(initPanel).toHaveBeenCalled();
        wrapper.rerender(_jsx(Wrapper, { lastSeekTime: 1 }));
        await act(async () => {
            await Promise.resolve();
        });
        wrapper.rerender(_jsx(Wrapper, { lastSeekTime: 1 }));
        await act(async () => {
            await Promise.resolve();
        });
        wrapper.rerender(_jsx(Wrapper, { lastSeekTime: 2 }));
        await act(async () => {
            await Promise.resolve();
        });
        expect(renderStates).toEqual([
            { currentFrame: [], didSeek: false }, // first frame is empty because there are no subscribers yet
            { currentFrame: [message], didSeek: true },
            { currentFrame: [message], didSeek: false },
            { currentFrame: [message], didSeek: true },
        ]);
        mockRAF.mockRestore();
    });
    it("should support advertising on a topic", async () => {
        const initPanel = (context) => {
            context.advertise?.("/some/topic", "some_datatype");
        };
        const sig = signal();
        let passed = false;
        render(_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: {
                        capabilities: [PlayerCapabilities.advertise],
                        topics: [],
                        datatypes: new Map(),
                        frame: {},
                        layout: "UnknownPanel!4co6n9d",
                        setPublishers: (id, advertisements) => {
                            if (passed) {
                                return;
                            }
                            expect(id).toBeDefined();
                            expect(advertisements).toEqual(expect.arrayContaining([
                                {
                                    topic: "/some/topic",
                                    schemaName: "some_datatype",
                                    options: undefined,
                                },
                            ]));
                            passed = true;
                            sig.resolve();
                        },
                    }, children: _jsx(PanelExtensionAdapter, { config: {}, saveConfig: () => { }, initPanel: initPanel }) }) }) }));
        await act(async () => undefined);
        await sig;
    });
    it("should support advertising on multiple topics", async () => {
        let count = 0;
        const initPanel = (context) => {
            context.advertise?.("/some/topic", "some_datatype");
            context.advertise?.("/another/topic", "another_datatype");
        };
        const sig = signal();
        render(_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: {
                        capabilities: [PlayerCapabilities.advertise],
                        topics: [],
                        datatypes: new Map(),
                        frame: {},
                        layout: "UnknownPanel!4co6n9d",
                        setPublishers: (id, advertisements) => {
                            expect(id).toBeDefined();
                            ++count;
                            if (count === 1) {
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect(advertisements).toEqual(
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect.arrayContaining([
                                    {
                                        topic: "/some/topic",
                                        schemaName: "some_datatype",
                                        options: undefined,
                                    },
                                ]));
                            }
                            else if (count === 2) {
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect(advertisements).toEqual(
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect.arrayContaining([
                                    {
                                        topic: "/some/topic",
                                        schemaName: "some_datatype",
                                        options: undefined,
                                    },
                                    {
                                        topic: "/another/topic",
                                        schemaName: "another_datatype",
                                        options: undefined,
                                    },
                                ]));
                                sig.resolve();
                            }
                        },
                    }, children: _jsx(PanelExtensionAdapter, { config: {}, saveConfig: () => { }, initPanel: initPanel }) }) }) }));
        await act(async () => undefined);
        await sig;
    });
    it("should support publishing on a topic", async () => {
        expect.assertions(3);
        const initPanel = (context) => {
            context.advertise?.("/some/topic", "some_datatype");
            context.publish?.("/some/topic", {
                foo: "bar",
            });
        };
        const sig = signal();
        let passed = false;
        render(_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: {
                        capabilities: [PlayerCapabilities.advertise],
                        topics: [],
                        datatypes: new Map(),
                        frame: {},
                        layout: "UnknownPanel!4co6n9d",
                        setPublishers: (id, advertisements) => {
                            if (passed) {
                                return;
                            }
                            expect(id).toBeDefined();
                            expect(advertisements).toEqual(expect.arrayContaining([
                                {
                                    topic: "/some/topic",
                                    schemaName: "some_datatype",
                                    options: undefined,
                                },
                            ]));
                        },
                        publish: (request) => {
                            if (passed) {
                                return;
                            }
                            expect(request).toEqual({ topic: "/some/topic", msg: { foo: "bar" } });
                            passed = true;
                            sig.resolve();
                        },
                    }, children: _jsx(PanelExtensionAdapter, { config: {}, saveConfig: () => { }, initPanel: initPanel }) }) }) }));
        await act(async () => undefined);
        await sig;
    });
    it("should support unadvertising", async () => {
        let count = 0;
        const initPanel = (context) => {
            context.advertise?.("/some/topic", "some_datatype");
            context.advertise?.("/another/topic", "another_datatype");
            context.unadvertise?.("/some/topic");
        };
        const sig = signal();
        render(_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: {
                        capabilities: [PlayerCapabilities.advertise],
                        topics: [],
                        datatypes: new Map(),
                        frame: {},
                        layout: "UnknownPanel!4co6n9d",
                        setPublishers: (id, advertisements) => {
                            expect(id).toBeDefined();
                            ++count;
                            if (count === 1) {
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect(advertisements).toEqual(
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect.arrayContaining([
                                    {
                                        topic: "/some/topic",
                                        schemaName: "some_datatype",
                                        options: undefined,
                                    },
                                ]));
                            }
                            else if (count === 2) {
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect(advertisements).toEqual(
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect.arrayContaining([
                                    {
                                        topic: "/some/topic",
                                        schemaName: "some_datatype",
                                        options: undefined,
                                    },
                                    {
                                        topic: "/another/topic",
                                        schemaName: "another_datatype",
                                        options: undefined,
                                    },
                                ]));
                            }
                            else if (count === 3) {
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect(advertisements).toEqual(
                                // eslint-disable-next-line jest/no-conditional-expect
                                expect.arrayContaining([
                                    {
                                        topic: "/another/topic",
                                        schemaName: "another_datatype",
                                        options: undefined,
                                    },
                                ]));
                                sig.resolve();
                            }
                        },
                    }, children: _jsx(PanelExtensionAdapter, { config: {}, saveConfig: () => { }, initPanel: initPanel }) }) }) }));
        await act(async () => undefined);
        await sig;
    });
    it("should unadvertise when unmounting", (done) => {
        expect.assertions(5);
        let count = 0;
        const initPanel = (context) => {
            expect(context).toBeDefined();
            context.advertise?.("/some/topic", "some_datatype");
        };
        const fixture = {
            capabilities: [PlayerCapabilities.advertise],
            topics: [],
            datatypes: new Map(),
            frame: {},
            layout: "UnknownPanel!4co6n9d",
            setPublishers: (id, advertisements) => {
                expect(id).toBeDefined();
                ++count;
                if (count === 1) {
                    // eslint-disable-next-line jest/no-conditional-expect
                    expect(advertisements).toEqual(
                    // eslint-disable-next-line jest/no-conditional-expect
                    expect.arrayContaining([
                        {
                            topic: "/some/topic",
                            schemaName: "some_datatype",
                            options: undefined,
                        },
                    ]));
                }
                else if (count === 2) {
                    // eslint-disable-next-line jest/no-conditional-expect
                    expect(advertisements).toEqual(expect.arrayContaining([]));
                    done();
                }
            },
        };
        const config = {};
        const saveConfig = () => { };
        const Wrapper = ({ mounted = true }) => {
            return (_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: fixture, children: mounted && (_jsx(PanelExtensionAdapter, { config: config, saveConfig: saveConfig, initPanel: initPanel })) }) }) }));
        };
        const handle = render(_jsx(Wrapper, { mounted: true }));
        handle.rerender(_jsx(Wrapper, { mounted: false }));
    });
    it("supports adding new panels to the layout", async () => {
        expect.assertions(3);
        const openSiblingPanel = jest.fn();
        const config = {};
        const saveConfig = () => { };
        const sig = signal();
        const initPanel = (context) => {
            expect(context).toBeDefined();
            expect(() => {
                context.layout.addPanel({
                    position: "foo",
                    type: "X",
                    updateIfExists: true,
                    getState: () => undefined,
                });
            }).toThrow();
            context.layout.addPanel({
                position: "sibling",
                type: "X",
                updateIfExists: true,
                getState: () => undefined,
            });
            expect(openSiblingPanel.mock.calls).toEqual([
                [{ panelType: "X", updateIfExists: true, siblingConfigCreator: expect.any(Function) }],
            ]);
            sig.resolve();
        };
        const Wrapper = () => {
            return (_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { openSiblingPanel: openSiblingPanel, children: _jsx(PanelSetup, { children: _jsx(PanelExtensionAdapter, { config: config, saveConfig: saveConfig, initPanel: initPanel }) }) }) }));
        };
        const handle = render(_jsx(Wrapper, {}));
        await act(async () => undefined);
        // force a re-render to make sure we call init panel once
        handle.rerender(_jsx(Wrapper, {}));
        await sig;
    });
    it("should unsubscribe from all topics when subscribing to empty topics array", async () => {
        const initPanel = (context) => {
            context.subscribe([]);
        };
        const sig = signal();
        render(_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: {
                        capabilities: [PlayerCapabilities.advertise],
                        topics: [],
                        datatypes: new Map(),
                        frame: {},
                        layout: "UnknownPanel!4co6n9d",
                        setSubscriptions: (_, payload) => {
                            expect(payload).toEqual([]);
                            sig.resolve();
                        },
                    }, children: _jsx(PanelExtensionAdapter, { config: {}, saveConfig: () => { }, initPanel: initPanel }) }) }) }));
        await act(async () => undefined);
        await sig;
    });
    it("should get and set variables", async () => {
        const mockRAF = jest
            .spyOn(window, "requestAnimationFrame")
            // eslint-disable-next-line @typescript-eslint/no-confusing-void-expression
            .mockImplementation((cb) => queueMicrotask(() => cb(performance.now())));
        let sequence = 0;
        const renderStates = [];
        const initPanel = jest.fn((context) => {
            context.watch("variables");
            context.onRender = (renderState, done) => {
                renderStates.push({ ...renderState });
                if (sequence === 0) {
                    context.setVariable("foo", "bar");
                }
                else if (sequence === 1) {
                    context.setVariable("foo", true);
                }
                else if (sequence === 2) {
                    context.setVariable("foo", { nested: [1, 2, 3] });
                }
                else if (sequence === 3) {
                    context.setVariable("foo", undefined);
                }
                sequence++;
                done();
            };
        });
        const config = {};
        const saveConfig = () => { };
        const Wrapper = () => {
            return (_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { children: _jsx(PanelExtensionAdapter, { config: config, saveConfig: saveConfig, initPanel: initPanel }) }) }) }));
        };
        const handle = render(_jsx(Wrapper, {}));
        handle.rerender(_jsx(Wrapper, {}));
        await act(async () => {
            await Promise.resolve();
        });
        handle.rerender(_jsx(Wrapper, {}));
        await act(async () => {
            await Promise.resolve();
        });
        handle.rerender(_jsx(Wrapper, {}));
        await act(async () => {
            await Promise.resolve();
        });
        handle.rerender(_jsx(Wrapper, {}));
        await act(async () => {
            await Promise.resolve();
        });
        expect(renderStates).toEqual([
            { variables: new Map() },
            { variables: new Map([["foo", "bar"]]) },
            { variables: new Map([["foo", true]]) },
            { variables: new Map([["foo", { nested: [1, 2, 3] }]]) },
            { variables: new Map() },
        ]);
        mockRAF.mockRestore();
    });
    it("should call pause frame with new frame and resume after rendering", async () => {
        const renderStates = [];
        const initPanel = jest.fn((context) => {
            context.watch("currentTime");
            context.onRender = (renderState, done) => {
                renderStates.push({ ...renderState });
                done();
            };
        });
        const config = {};
        const saveConfig = () => { };
        const pauseFrameCond = new Condvar();
        const Wrapper = ({ currentTime }) => {
            return (_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: {
                            activeData: { currentTime },
                        }, pauseFrame: () => {
                            return () => {
                                pauseFrameCond.notifyAll();
                            };
                        }, children: _jsx(PanelExtensionAdapter, { config: config, saveConfig: saveConfig, initPanel: initPanel }) }) }) }));
        };
        // Setup the request animation frame to take some time
        const mockRAF = jest
            .spyOn(window, "requestAnimationFrame")
            // eslint-disable-next-line @typescript-eslint/no-confusing-void-expression
            .mockImplementation((cb) => queueMicrotask(() => cb(performance.now())));
        const resumeFrameWait = pauseFrameCond.wait();
        render(_jsx(Wrapper, { currentTime: { sec: 1, nsec: 0 } }));
        expect(initPanel).toHaveBeenCalled();
        await act(async () => {
            await resumeFrameWait;
        });
        expect(renderStates).toEqual([
            {
                currentTime: { sec: 1, nsec: 0 },
            },
        ]);
        mockRAF.mockRestore();
    });
    it("ignores subscriptions after panel unmount", async () => {
        const sig = signal();
        const initPanel = jest.fn((context) => {
            context.watch("currentFrame");
            context.subscribe(["x"]);
            setTimeout(() => {
                context.subscribe(["y"]);
                sig.resolve();
            }, 10);
        });
        const config = {};
        const saveConfig = () => { };
        const mockSetSubscriptions = jest.fn();
        const { unmount } = render(_jsx(ThemeProvider, { isDark: true, children: _jsx(MockPanelContextProvider, { children: _jsx(PanelSetup, { fixture: { setSubscriptions: mockSetSubscriptions }, children: _jsx(PanelExtensionAdapter, { config: config, saveConfig: saveConfig, initPanel: initPanel }) }) }) }));
        expect(initPanel).toHaveBeenCalled();
        expect(mockSetSubscriptions.mock.calls).toEqual([
            [expect.any(String), [{ preloadType: "full", topic: "x" }]],
        ]);
        unmount();
        expect(mockSetSubscriptions.mock.calls).toEqual([
            [expect.any(String), [{ preloadType: "full", topic: "x" }]],
            [expect.any(String), []],
        ]);
        await act(async () => {
            await sig;
        });
        unmount();
        expect(mockSetSubscriptions.mock.calls).toEqual([
            [expect.any(String), [{ preloadType: "full", topic: "x" }]],
            [expect.any(String), []],
        ]);
    });
});
