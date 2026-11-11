/// <reference types="react" />
/**
 * Encapsulates logic for directly updating topic stats DOM elements, bypassing
 * react for performance. To use this component mount it directly under your component
 * containing topics you want to update. Tag each topic stat field with data-topic
 * and data-topic-stat attributes.
 *
 * @property interval - the interval, in frames, between updates.
 */
export declare function DirectTopicStatsUpdater({ interval }: {
    interval?: number;
}): JSX.Element;
