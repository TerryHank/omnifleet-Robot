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
import { v4 as uuidv4 } from "uuid";
import { debouncePromise } from "@foxglove/den/async";
import { filterMap } from "@foxglove/den/collection";
import Log from "@foxglove/log";
import roslib from "@foxglove/roslibjs";
import { parse as parseMessageDefinition } from "@foxglove/rosmsg";
import { MessageReader as ROS1MessageReader } from "@foxglove/rosmsg-serialization";
import { MessageReader as ROS2MessageReader } from "@foxglove/rosmsg2-serialization";
import { fromMillis, toSec } from "@foxglove/rostime";
import PlayerProblemManager from "@foxglove/studio-base/players/PlayerProblemManager";
import { PlayerCapabilities, PlayerPresence, } from "@foxglove/studio-base/players/types";
import { bagConnectionsToDatatypes } from "@foxglove/studio-base/util/bagConnectionsHelper";
const log = Log.getLogger(__dirname);
const CAPABILITIES = [PlayerCapabilities.advertise, PlayerCapabilities.callServices];
function collateNodeDetails(details, key) {
    return _.transform(details, (acc, detail) => {
        const { node, values } = detail[key];
        for (const value of values) {
            if (!acc.has(value)) {
                acc.set(value, new Set());
            }
            acc.get(value)?.add(node);
        }
    }, new Map());
}
function isClockMessage(topic, msg) {
    const maybeClockMsg = msg;
    return topic === "/clock" && maybeClockMsg.clock != undefined && !isNaN(maybeClockMsg.clock.sec);
}
function isRecord(value) {
    return typeof value === "object" && value != undefined;
}
// Connects to `rosbridge_server` instance using `roslibjs`. Currently doesn't support seeking or
// showing simulated time, so current time from Date.now() is always used instead. Also doesn't yet
// support raw ROS messages; instead we use the CBOR compression provided by roslibjs, which
// unmarshalls into plain JS objects.
export default class RosbridgePlayer {
    #url; // WebSocket URL.
    #rosClient; // The roslibjs client when we're connected.
    #id = uuidv4(); // Unique ID for this player.
    #isRefreshing = false; // True if currently refreshing the node graph.
    #listener; // Listener for _emitState().
    #closed = false; // Whether the player has been completely closed using close().
    #providerTopics; // Topics as published by the WebSocket.
    #providerTopicsStats = new Map(); // topic names to topic statistics.
    #providerDatatypes; // Datatypes as published by the WebSocket.
    #publishedTopics = new Map(); // A map of topic names to the set of publisher IDs publishing each topic.
    #subscribedTopics = new Map(); // A map of topic names to the set of subscriber IDs subscribed to each topic.
    #services = new Map(); // A map of service names to service provider IDs that provide each service.
    #messageReadersByDatatype = {};
    #start; // The time at which we started playing.
    #clockTime; // The most recent published `/clock` time, if available
    // active subscriptions
    #topicSubscriptions = new Map();
    #requestedSubscriptions = []; // Requested subscriptions by setSubscriptions()
    #parsedMessages = []; // Queue of messages that we'll send in next _emitState() call.
    #requestTopicsTimeout; // setTimeout() handle for _requestTopics().
    // active publishers for the current connection
    #topicPublishers = new Map();
    // which topics we want to advertise to other nodes
    #advertisements = [];
    #parsedTopics = new Set();
    #receivedBytes = 0;
    #metricsCollector;
    #presence = PlayerPresence.NOT_PRESENT;
    #problems = new PlayerProblemManager();
    #emitTimer;
    #serviceTypeCache = new Map();
    #sourceId;
    #rosVersion;
    constructor({ url, metricsCollector, sourceId, }) {
        this.#presence = PlayerPresence.INITIALIZING;
        this.#metricsCollector = metricsCollector;
        this.#url = url;
        this.#start = fromMillis(Date.now());
        this.#metricsCollector.playerConstructed();
        this.#sourceId = sourceId;
        this.#open();
    }
    #open = () => {
        if (this.#closed) {
            return;
        }
        if (this.#rosClient != undefined) {
            throw new Error(`Attempted to open a second Rosbridge connection`);
        }
        this.#problems.removeProblem("rosbridge:connection-failed");
        log.info(`Opening connection to ${this.#url}`);
        // `workersocket` will open the actual WebSocket connection in a WebWorker.
        const rosClient = new roslib.Ros({ url: this.#url, transportLibrary: "workersocket" });
        rosClient.on("connection", () => {
            log.info(`Connected to ${this.#url}`);
            if (this.#closed) {
                return;
            }
            this.#presence = PlayerPresence.PRESENT;
            this.#problems.removeProblem("rosbridge:connection-failed");
            this.#rosClient = rosClient;
            this.#setupPublishers();
            void this.#requestTopics({ forceUpdate: true });
        });
        rosClient.on("error", (err) => {
            if (err) {
                this.#problems.addProblem("rosbridge:error", {
                    severity: "warn",
                    message: "Rosbridge error",
                    error: err,
                });
                this.#emitState();
            }
        });
        rosClient.on("close", () => {
            this.#presence = PlayerPresence.RECONNECTING;
            if (this.#requestTopicsTimeout) {
                clearTimeout(this.#requestTopicsTimeout);
            }
            for (const [topicName, topic] of this.#topicSubscriptions) {
                topic.unsubscribe();
                this.#topicSubscriptions.delete(topicName);
            }
            rosClient.close(); // ensure the underlying worker is cleaned up
            this.#rosClient = undefined;
            this.#problems.addProblem("rosbridge:connection-failed", {
                severity: "error",
                message: "Connection failed",
                tip: `Check that the rosbridge WebSocket server at ${this.#url} is reachable.`,
            });
            this.#emitState();
            // Try connecting again.
            setTimeout(this.#open, 3000);
        });
    };
    #topicsChanged = (newTopics) => {
        if (!this.#providerTopics || newTopics.length !== this.#providerTopics.length) {
            return true;
        }
        return !_.isEqual(this.#providerTopics, newTopics);
    };
    async #requestTopics(opt) {
        const { forceUpdate = false } = opt ?? {};
        // clear problems before each topics request so we don't have stale problems from previous failed requests
        this.#problems.removeProblems((id) => id.startsWith("requestTopics:"));
        if (this.#requestTopicsTimeout) {
            clearTimeout(this.#requestTopicsTimeout);
        }
        const rosClient = this.#rosClient;
        if (!rosClient || this.#closed) {
            return;
        }
        // getTopicsAndRawTypes might silently hang. When this happens, there is no indication to the user
        // that the connection is doing anything and studio shows no errors and no data.
        // This logic adds a warning after 5 seconds (picked arbitrarily) to display a notice to the user.
        const topicsStallWarningTimeout = setTimeout(() => {
            this.#problems.addProblem("topicsAndRawTypesTimeout", {
                severity: "warn",
                message: "Taking too long to get topics and raw types.",
            });
            this.#emitState();
        }, 5000);
        try {
            const result = await new Promise((resolve, reject) => {
                rosClient.getTopicsAndRawTypes(resolve, reject);
            });
            clearTimeout(topicsStallWarningTimeout);
            this.#problems.removeProblem("topicsAndRawTypesTimeout");
            const topicsMissingDatatypes = [];
            const topics = [];
            const datatypeDescriptions = [];
            const messageReaders = {};
            // Automatically detect the ROS version based on the datatypes.
            // The rosbridge server itself publishes /rosout so the topic should be reliably present.
            if (result.types.includes("rcl_interfaces/msg/Log")) {
                this.#rosVersion = 2;
                this.#problems.removeProblem("unknownRosVersion");
            }
            else if (result.types.includes("rosgraph_msgs/Log")) {
                this.#rosVersion = 1;
                this.#problems.removeProblem("unknownRosVersion");
            }
            else {
                this.#rosVersion = 1;
                this.#problems.addProblem("unknownRosVersion", {
                    severity: "warn",
                    message: "Unable to detect ROS version, assuming ROS 1",
                });
            }
            for (let i = 0; i < result.topics.length; i++) {
                const topicName = result.topics[i];
                const type = result.types[i];
                const messageDefinition = result.typedefs_full_text[i];
                if (type == undefined || messageDefinition == undefined) {
                    topicsMissingDatatypes.push(topicName);
                    continue;
                }
                topics.push({ name: topicName, schemaName: type });
                datatypeDescriptions.push({ type, messageDefinition });
                const parsedDefinition = parseMessageDefinition(messageDefinition, {
                    ros2: this.#rosVersion === 2,
                });
                // https://github.com/typescript-eslint/typescript-eslint/issues/6632
                if (!messageReaders[type]) {
                    messageReaders[type] =
                        this.#rosVersion !== 2
                            ? new ROS1MessageReader(parsedDefinition)
                            : new ROS2MessageReader(parsedDefinition);
                }
            }
            // We call requestTopics on a timeout to check for new topics. If there are no changes to topics
            // we want to bail and avoid updating readers, subscribers, etc.
            // However, during a re-connect, we _do_ want to refresh this list and re-subscribe
            const sortedTopics = _.sortBy(topics, "name");
            if (!forceUpdate && !this.#topicsChanged(sortedTopics)) {
                return;
            }
            if (topicsMissingDatatypes.length > 0) {
                this.#problems.addProblem("requestTopics:missing-types", {
                    severity: "warn",
                    message: "Could not resolve all message types",
                    tip: `Message types could not be found for these topics: ${topicsMissingDatatypes.join(",")}`,
                });
            }
            // Remove stats entries for removed topics
            const topicsSet = new Set(topics.map((topic) => topic.name));
            for (const topic of this.#providerTopicsStats.keys()) {
                if (!topicsSet.has(topic)) {
                    this.#providerTopicsStats.delete(topic);
                }
            }
            this.#providerTopics = sortedTopics;
            this.#providerDatatypes = bagConnectionsToDatatypes(datatypeDescriptions, {
                ros2: this.#rosVersion === 2,
            });
            this.#messageReadersByDatatype = messageReaders;
            // Try subscribing again, since we might now be able to subscribe to some new topics.
            this.setSubscriptions(this.#requestedSubscriptions);
            // Refresh the full graph topology
            this.#refreshSystemState().catch((error) => {
                log.error(error);
            });
        }
        catch (error) {
            log.error(error);
            clearTimeout(topicsStallWarningTimeout);
            this.#problems.removeProblem("topicsAndRawTypesTimeout");
            this.#problems.addProblem("requestTopics:error", {
                severity: "error",
                message: "Failed to fetch topics from rosbridge",
                error,
            });
        }
        finally {
            this.#emitState();
            // Regardless of what happens, request topics again in a little bit.
            this.#requestTopicsTimeout = setTimeout(() => void this.#requestTopics(), 3000);
        }
    }
    // Potentially performance-sensitive; await can be expensive
    // eslint-disable-next-line @typescript-eslint/promise-function-async
    #emitState = debouncePromise(() => {
        if (!this.#listener || this.#closed) {
            return Promise.resolve();
        }
        const providerTopics = this.#providerTopics;
        const providerDatatypes = this.#providerDatatypes;
        const start = this.#start;
        if (!providerTopics || !providerDatatypes || !start) {
            return this.#listener({
                name: this.#url,
                presence: this.#presence,
                progress: {},
                capabilities: CAPABILITIES,
                profile: undefined,
                playerId: this.#id,
                activeData: undefined,
                problems: this.#problems.problems(),
                urlState: {
                    sourceId: this.#sourceId,
                    parameters: { url: this.#url },
                },
            });
        }
        // When connected
        // Time is always moving forward even if we don't get messages from the server.
        if (this.#presence === PlayerPresence.PRESENT) {
            if (this.#emitTimer != undefined) {
                clearTimeout(this.#emitTimer);
            }
            this.#emitTimer = setTimeout(this.#emitState, 100);
        }
        const currentTime = this.#getCurrentTime();
        const messages = this.#parsedMessages;
        this.#parsedMessages = [];
        return this.#listener({
            name: this.#url,
            presence: this.#presence,
            progress: {},
            capabilities: CAPABILITIES,
            profile: this.#rosVersion === 2 ? "ros2" : "ros1",
            playerId: this.#id,
            problems: this.#problems.problems(),
            urlState: {
                sourceId: this.#sourceId,
                parameters: { url: this.#url },
            },
            activeData: {
                messages,
                totalBytesReceived: this.#receivedBytes,
                startTime: start,
                endTime: currentTime,
                currentTime,
                isPlaying: true,
                speed: 1,
                // We don't support seeking, so we need to set this to any fixed value. Just avoid 0 so
                // that we don't accidentally hit falsy checks.
                lastSeekTime: 1,
                topics: providerTopics,
                // Always copy topic stats since message counts and timestamps are being updated
                topicStats: new Map(this.#providerTopicsStats),
                datatypes: providerDatatypes,
                publishedTopics: this.#publishedTopics,
                subscribedTopics: this.#subscribedTopics,
                services: this.#services,
            },
        });
    });
    setListener(listener) {
        this.#listener = listener;
        this.#emitState();
    }
    close() {
        this.#closed = true;
        if (this.#rosClient) {
            this.#rosClient.close();
        }
        if (this.#emitTimer != undefined) {
            clearTimeout(this.#emitTimer);
            this.#emitTimer = undefined;
        }
    }
    setSubscriptions(subscriptions) {
        this.#requestedSubscriptions = subscriptions;
        if (!this.#rosClient || this.#closed) {
            return;
        }
        // Subscribe to additional topics used by RosbridgePlayer itself
        this.#addInternalSubscriptions(subscriptions);
        this.#parsedTopics = new Set(subscriptions.map(({ topic }) => topic));
        // See what topics we actually can subscribe to.
        const availableTopicsByTopicName = _.keyBy(this.#providerTopics ?? [], ({ name }) => name);
        const topicNames = subscriptions
            .map(({ topic }) => topic)
            .filter((topicName) => availableTopicsByTopicName[topicName]);
        // Subscribe to all topics that we aren't subscribed to yet.
        for (const topicName of topicNames) {
            if (this.#topicSubscriptions.has(topicName)) {
                continue;
            }
            const topic = new roslib.Topic({
                ros: this.#rosClient,
                name: topicName,
                compression: "cbor-raw",
            });
            const availTopic = availableTopicsByTopicName[topicName];
            if (!availTopic) {
                continue;
            }
            const { schemaName } = availTopic;
            const messageReader = this.#messageReadersByDatatype[schemaName];
            if (!messageReader) {
                continue;
            }
            const problemId = `message:${topicName}`;
            topic.subscribe((message) => {
                if (!this.#providerTopics) {
                    return;
                }
                try {
                    const buffer = message.bytes;
                    const bytes = new Uint8Array(buffer);
                    const innerMessage = messageReader.readMessage(bytes);
                    // handle clock messages before choosing receiveTime so the clock can set its own receive time
                    if (isClockMessage(topicName, innerMessage)) {
                        const time = innerMessage.clock;
                        const seconds = toSec(innerMessage.clock);
                        if (!isNaN(seconds)) {
                            if (this.#clockTime == undefined) {
                                this.#start = time;
                            }
                            this.#clockTime = time;
                        }
                    }
                    const receiveTime = this.#getCurrentTime();
                    if (this.#parsedTopics.has(topicName)) {
                        const msg = {
                            topic: topicName,
                            receiveTime,
                            message: innerMessage,
                            schemaName,
                            sizeInBytes: bytes.byteLength,
                        };
                        this.#parsedMessages.push(msg);
                    }
                    this.#problems.removeProblem(problemId);
                    // Update the message count for this topic
                    let stats = this.#providerTopicsStats.get(topicName);
                    if (this.#topicSubscriptions.has(topicName)) {
                        if (!stats) {
                            stats = { numMessages: 0 };
                            this.#providerTopicsStats.set(topicName, stats);
                        }
                        stats.numMessages++;
                    }
                }
                catch (error) {
                    this.#problems.addProblem(problemId, {
                        severity: "error",
                        message: `Failed to parse message on ${topicName}`,
                        error,
                    });
                }
                this.#emitState();
            });
            this.#topicSubscriptions.set(topicName, topic);
        }
        // Unsubscribe from topics that we are subscribed to but shouldn't be.
        for (const [topicName, topic] of this.#topicSubscriptions) {
            if (!topicNames.includes(topicName)) {
                topic.unsubscribe();
                this.#topicSubscriptions.delete(topicName);
                // Reset the message count for this topic
                this.#providerTopicsStats.delete(topicName);
            }
        }
    }
    setPublishers(publishers) {
        // Since `setPublishers` is rarely called, we can get away with just throwing away the old
        // Roslib.Topic objects and creating new ones.
        for (const publisher of this.#topicPublishers.values()) {
            publisher.unadvertise();
        }
        this.#topicPublishers.clear();
        this.#advertisements = publishers;
        this.#setupPublishers();
    }
    setParameter(_key, _value) {
        throw new Error("Parameter editing is not supported by the Rosbridge connection");
    }
    publish({ topic, msg }) {
        const publisher = this.#topicPublishers.get(topic);
        if (!publisher) {
            if (this.#advertisements.some((opts) => opts.topic === topic)) {
                // Topic was advertised but the connection is not yet established
                return;
            }
            throw new Error(`Tried to publish on a topic that is not registered as a publisher: ${topic}`);
        }
        publisher.publish(msg);
    }
    // Query the type name for this service. Cache the query to avoid looking it up again.
    async #getServiceType(service) {
        if (!this.#rosClient) {
            throw new Error("Not connected");
        }
        const existing = this.#serviceTypeCache.get(service);
        if (existing) {
            return await existing;
        }
        const rosClient = this.#rosClient;
        const serviceTypePromise = new Promise((resolve, reject) => {
            rosClient.getServiceType(service, resolve, reject);
        });
        this.#serviceTypeCache.set(service, serviceTypePromise);
        return await serviceTypePromise;
    }
    async callService(service, request) {
        if (!this.#rosClient) {
            throw new Error("Not connected");
        }
        if (!isRecord(request)) {
            throw new Error("RosbridgePlayer#callService request must be an object");
        }
        const serviceType = await this.#getServiceType(service);
        // Create a proxy object for dispatching our service call
        const proxy = new roslib.Service({
            ros: this.#rosClient,
            name: service,
            serviceType,
        });
        // Send the service request
        return await new Promise((resolve, reject) => {
            proxy.callService(request, (response) => {
                resolve(response);
            }, (error) => {
                reject(error);
            });
        });
    }
    // Bunch of unsupported stuff. Just don't do anything for these.
    startPlayback() {
        // no-op
    }
    pausePlayback() {
        // no-op
    }
    seekPlayback(_time) {
        // no-op
    }
    setPlaybackSpeed(_speedFraction) {
        // no-op
    }
    setGlobalVariables() {
        // no-op
    }
    #setupPublishers() {
        // This function will be called again once a connection is established
        if (!this.#rosClient) {
            return;
        }
        if (this.#advertisements.length <= 0) {
            return;
        }
        for (const { topic, schemaName: datatype } of this.#advertisements) {
            const roslibTopic = new roslib.Topic({
                ros: this.#rosClient,
                name: topic,
                messageType: datatype,
                queue_size: 0,
            });
            this.#topicPublishers.set(topic, roslibTopic);
            roslibTopic.advertise();
        }
    }
    #addInternalSubscriptions(subscriptions) {
        // Always subscribe to /clock if available
        if (subscriptions.find((sub) => sub.topic === "/clock") == undefined) {
            subscriptions.unshift({
                topic: "/clock",
            });
        }
    }
    #getCurrentTime() {
        return this.#clockTime ?? fromMillis(Date.now());
    }
    // Refreshes the full system state graph. Runs in the background so we don't
    // block app startup while mapping large node graphs.
    async #refreshSystemState() {
        if (this.#isRefreshing) {
            return;
        }
        try {
            this.#isRefreshing = true;
            const nodes = await new Promise((resolve, reject) => {
                this.#rosClient?.getNodes((fetchedNodes) => {
                    resolve(fetchedNodes);
                }, reject);
            });
            const promises = nodes.map(async (node) => {
                return await new Promise((resolve, reject) => {
                    this.#rosClient?.getNodeDetails(node, (subscriptions, publications, services) => {
                        resolve({
                            publications: { node, values: publications },
                            services: { node, values: services },
                            subscriptions: { node, values: subscriptions },
                        });
                    }, reject);
                });
            });
            const results = await Promise.allSettled(promises);
            const fulfilled = filterMap(results, (item) => item.status === "fulfilled" ? item.value : undefined);
            this.#publishedTopics = collateNodeDetails(fulfilled, "publications");
            this.#subscribedTopics = collateNodeDetails(fulfilled, "subscriptions");
            this.#services = collateNodeDetails(fulfilled, "services");
            this.#emitState();
        }
        catch (error) {
            this.#problems.addProblem("requestTopics:system-state", {
                severity: "error",
                message: "Failed to fetch node details from rosbridge",
                error,
            });
        }
        finally {
            this.#isRefreshing = false;
        }
    }
}
