import { Time } from "@foxglove/rostime";
/**
 * Parses a ROS time (UNIX timestamp) containing a whole or floating point number of seconds. If
 * more than 9 digits of nanoseconds are given, the rest will be truncated.
 *
 * Parsing is lenient: if the numeric value given is too large and contains no decimal point, assume
 * it is ms, µs, ns instead of seconds (or a smaller unit, in powers of 1000).
 */
export default function parseFuzzyRosTime(stamp: string): Time | undefined;
