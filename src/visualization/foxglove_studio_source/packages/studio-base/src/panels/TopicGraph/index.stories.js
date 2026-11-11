import { jsx as _jsx } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { useAsync } from "react-use";
import PanelSetup from "@foxglove/studio-base/stories/PanelSetup";
import delay from "@foxglove/studio-base/util/delay";
import TopicGraph from "./index";
export default {
    title: "panels/TopicGraph",
    component: TopicGraph,
};
export const Empty = {
    render: () => {
        return (_jsx(PanelSetup, { children: _jsx(TopicGraph, {}) }));
    },
};
export const WithSettings = {
    render: function Story() {
        return (_jsx(PanelSetup, { includeSettings: true, children: _jsx(TopicGraph, {}) }));
    },
    parameters: {
        colorScheme: "light",
    },
};
function TopicsStory({ topicVisibility: initialTopicVisibility, }) {
    const [fixture] = useState({
        frame: {},
        topics: [{ name: "/topic", schemaName: "std_msgs/Header" }],
        activeData: {
            publishedTopics: new Map([
                ["/topic", new Set(["pub-1", "pub-2"])],
                ["/topic_without_subscriber", new Set(["pub-1", "pub-2"])],
            ]),
            subscribedTopics: new Map([["/topic", new Set(["sub-1"])]]),
        },
    });
    useAsync(async () => {
        await delay(10);
        document.querySelector(`[data-testid="set-topic-visibility"] button`).click();
        const radioOption = document.querySelector(`[data-testid="${initialTopicVisibility}"]`);
        if (radioOption) {
            radioOption.click();
            document
                .querySelector(`[data-testid="set-topic-visibility"] div button:last-child`)
                .click();
        }
    }, [initialTopicVisibility]);
    return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(TopicGraph, {}) }));
}
export const AllTopics = {
    render: () => _jsx(TopicsStory, { topicVisibility: "all" }),
};
export const TopicsWithSubscribers = {
    render: () => _jsx(TopicsStory, { topicVisibility: "subscribed" }),
};
export const TopicsHidden = {
    render: () => _jsx(TopicsStory, { topicVisibility: "none" }),
};
export const ReLayout = {
    render: function Story() {
        const [fixture, setFixture] = useState({
            frame: {},
            topics: [{ name: "/topic", schemaName: "std_msgs/Header" }],
            activeData: {
                publishedTopics: new Map([["/topic", new Set(["pub-1", "pub-2"])]]),
                subscribedTopics: new Map([["/topic", new Set(["sub-1"])]]),
            },
        });
        useEffect(() => {
            const timeOutID = setTimeout(() => {
                setFixture({
                    frame: {},
                    topics: [{ name: "/topic", schemaName: "std_msgs/Header" }],
                    activeData: {
                        publishedTopics: new Map([["/topic", new Set(["pub-1", "pub-2"])]]),
                        subscribedTopics: new Map([["/topic", new Set(["sub-1", "sub-2"])]]),
                    },
                });
            }, 100);
            return () => {
                clearTimeout(timeOutID);
            };
        }, []);
        return (_jsx(PanelSetup, { fixture: fixture, children: _jsx(TopicGraph, {}) }));
    },
    parameters: {
        chromatic: {
            delay: 200,
        },
    },
};
