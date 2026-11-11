import { jsx as _jsx } from "react/jsx-runtime";
import * as _ from "lodash-es";
import { useEffect, useMemo, useRef, useState } from "react";
import shallowequal from "shallowequal";
import { createStore } from "zustand";
import { Condvar } from "@foxglove/den/async";
import { isLessThan } from "@foxglove/rostime";
import { pauseFrameForPromises, } from "@foxglove/studio-base/components/MessagePipeline/pauseFrameForPromise";
import { PlayerCapabilities, PlayerPresence, } from "@foxglove/studio-base/players/types";
import { ContextInternal } from "./index";
import { reducer } from "./store";
import { makeSubscriptionMemoizer } from "./subscriptions";
const NO_DATATYPES = new Map();
function noop() { }
function getPublicState(prevState, props, dispatch, promisesToWaitForRef) {
    let startTime = prevState?.public.playerState.activeData?.startTime;
    let currentTime = props.currentTime;
    if (!currentTime) {
        for (const message of props.messages ?? []) {
            if (startTime == undefined || isLessThan(message.receiveTime, startTime)) {
                startTime = message.receiveTime;
            }
            if (!currentTime || isLessThan(currentTime, message.receiveTime)) {
                currentTime = message.receiveTime;
            }
        }
    }
    return {
        playerState: {
            name: props.name,
            presence: props.presence ?? PlayerPresence.PRESENT,
            playerId: props.playerId ?? "1",
            progress: props.progress ?? {},
            capabilities: props.capabilities ?? prevState?.public.playerState.capabilities ?? [],
            profile: props.profile,
            problems: props.problems,
            urlState: props.urlState,
            activeData: props.noActiveData === true
                ? undefined
                : {
                    messages: props.messages ?? [],
                    topics: props.topics ?? [],
                    topicStats: props.topicStats ?? new Map(),
                    datatypes: props.datatypes ?? NO_DATATYPES,
                    startTime: props.startTime ?? startTime ?? { sec: 100, nsec: 0 },
                    currentTime: currentTime ?? { sec: 100, nsec: 0 },
                    endTime: props.endTime ?? currentTime ?? { sec: 100, nsec: 0 },
                    isPlaying: props.isPlaying ?? false,
                    speed: 0.2,
                    lastSeekTime: 0,
                    totalBytesReceived: 0,
                    ...props.activeData,
                },
        },
        subscriptions: [],
        sortedTopics: props.topics === prevState?.mockProps.topics
            ? prevState?.public.sortedTopics ?? []
            : props.topics
                ? [...props.topics].sort((a, b) => a.name.localeCompare(b.name))
                : [],
        datatypes: props.datatypes ?? NO_DATATYPES,
        setSubscriptions: (props.setSubscriptions === prevState?.mockProps.setSubscriptions
            ? prevState?.public.setSubscriptions
            : undefined) ??
            ((id, payloads) => {
                dispatch({ type: "update-subscriber", id, payloads });
                props.setSubscriptions?.(id, payloads);
            }),
        setPublishers: (props.setPublishers === prevState?.mockProps.setPublishers
            ? prevState?.public.setPublishers
            : undefined) ??
            ((id, payloads) => {
                dispatch({ type: "set-publishers", id, payloads });
                props.setPublishers?.(id, payloads);
            }),
        setParameter: props.setParameter ?? noop,
        publish: props.publish ?? noop,
        callService: props.callService ?? (async () => { }),
        fetchAsset: props.fetchAsset ??
            (async () => {
                throw new Error(`not supported`);
            }),
        startPlayback: props.startPlayback,
        playUntil: noop,
        pausePlayback: props.pausePlayback,
        setPlaybackSpeed: props.capabilities?.includes(PlayerCapabilities.setSpeed) === true ? noop : undefined,
        seekPlayback: props.seekPlayback,
        pauseFrame: props.pauseFrame ??
            function (name) {
                const condvar = new Condvar();
                promisesToWaitForRef.current.push({ name, promise: condvar.wait() });
                return () => {
                    condvar.notifyAll();
                };
            },
    };
}
export default function MockMessagePipelineProvider(props) {
    const promisesToWaitForRef = useRef([]);
    const startTime = useRef();
    let currentTime = props.currentTime;
    if (!currentTime) {
        for (const message of props.messages ?? []) {
            if (startTime.current == undefined || isLessThan(message.receiveTime, startTime.current)) {
                startTime.current = message.receiveTime;
            }
            if (!currentTime || isLessThan(currentTime, message.receiveTime)) {
                currentTime = message.receiveTime;
            }
        }
    }
    const [hasSubscribers, setHasSubscribers] = useState(false);
    const mockProps = useMemo(() => {
        // only include messages in props once we have subscribers, to reflect actual behavior of player
        // and to prevent messages from being emitted before subscribers are set, so that they can go to their respective subscribers
        if (hasSubscribers) {
            const propsNoChildren = _.omit(props, "children");
            // mimic seek backfill behavior that happens after new subscribers are added.
            // note that for the mock use-case that this will only happen the first time subscribers are added, since we don't reset `hasSubscribers`
            if (props.noActiveData === true) {
                return propsNoChildren;
            }
            const activeData = {
                ...propsNoChildren.activeData,
            };
            activeData.lastSeekTime = (activeData.lastSeekTime ?? 0) + 1;
            return {
                ...propsNoChildren,
                activeData,
            };
        }
        return _.omit(props, ["children", "messages"]);
    }, [props, hasSubscribers]);
    const [store] = useState(() => createStore((set) => {
        const dispatch = async (action) => {
            const promisesToWaitFor = promisesToWaitForRef.current;
            if (promisesToWaitFor.length > 0) {
                await pauseFrameForPromises(promisesToWaitFor);
                // normally in the player listener this comes before the await, but when working with stories this hasn't been enough
                // so for this case we'll wait until all promises have resolved before clearing them
                promisesToWaitForRef.current = [];
            }
            if (action.type === "set-mock-props") {
                set((state) => {
                    const actionMockProps = action.mockProps;
                    if (shallowequal(state.mockProps, actionMockProps)) {
                        return state;
                    }
                    const publicState = getPublicState(state, actionMockProps, state.dispatch, promisesToWaitForRef);
                    const newState = reducer(state, {
                        type: "update-player-state",
                        playerState: publicState.playerState,
                    });
                    return {
                        ...newState,
                        mockProps: actionMockProps,
                        dispatch: state.dispatch,
                        public: {
                            ...publicState,
                            messageEventsBySubscriberId: newState.public.messageEventsBySubscriberId,
                        },
                    };
                });
            }
            else {
                set((state) => {
                    const newState = reducer(state, action);
                    if (!hasSubscribers &&
                        action.type === "update-subscriber" &&
                        action.payloads.length > 0) {
                        setHasSubscribers(true);
                    }
                    return { ...newState, dispatch: state.dispatch };
                });
            }
        };
        const reset = () => {
            throw new Error("not implemented");
        };
        const initialPublicState = getPublicState(undefined, mockProps, dispatch, promisesToWaitForRef);
        return {
            mockProps,
            player: undefined,
            dispatch,
            reset,
            subscriptionMemoizer: makeSubscriptionMemoizer(),
            publishersById: {},
            allPublishers: [],
            subscriptionsById: new Map(),
            subscriberIdsByTopic: new Map(),
            newTopicsBySubscriberId: new Map(),
            lastMessageEventByTopic: new Map(),
            lastCapabilities: [...initialPublicState.playerState.capabilities],
            public: {
                ...initialPublicState,
                messageEventsBySubscriberId: new Map(),
            },
        };
    }));
    // Can't be useLayoutEffect because we want child useEffect calls to resolve first to set subscribers
    // That way we can call `set-mock-props` after subscribers have been set, and we can emit messages that were subscribed to
    // If we `useLayoutEffect`, it will emit the initial messages with no subscribers set, which is not consistent with the real behavior
    useEffect(() => {
        store.getState().dispatch({ type: "set-mock-props", mockProps });
    }, [mockProps, store]);
    return _jsx(ContextInternal.Provider, { value: store, children: props.children });
}
