import { jsx as _jsx } from "react/jsx-runtime";
import { AppSetting } from "@foxglove/studio-base/AppSetting";
import { useMessagePipeline, } from "@foxglove/studio-base/components/MessagePipeline";
import { useAppTimeFormat } from "@foxglove/studio-base/hooks";
import { useAppConfigurationValue } from "@foxglove/studio-base/hooks/useAppConfigurationValue";
import { UnconnectedPlaybackTimeDisplay } from "./UnconnectedPlaybackTimeDisplay";
const selectIsPlaying = (ctx) => ctx.playerState.activeData?.isPlaying;
const selectStartTime = (ctx) => ctx.playerState.activeData?.startTime;
const selectEndTime = (ctx) => ctx.playerState.activeData?.endTime;
const selectCurrentTime = (ctx) => ctx.playerState.activeData?.currentTime;
export default function PlaybackTimeDisplay(props) {
    const [timezone] = useAppConfigurationValue(AppSetting.TIMEZONE);
    const isPlaying = useMessagePipeline(selectIsPlaying);
    const startTime = useMessagePipeline(selectStartTime);
    const endTime = useMessagePipeline(selectEndTime);
    const currentTime = useMessagePipeline(selectCurrentTime);
    const appTimeFormat = useAppTimeFormat();
    return (_jsx(UnconnectedPlaybackTimeDisplay, { appTimeFormat: appTimeFormat, currentTime: currentTime, startTime: startTime, endTime: endTime, onSeek: props.onSeek, onPause: props.onPause, isPlaying: isPlaying ?? false, timezone: timezone }));
}
