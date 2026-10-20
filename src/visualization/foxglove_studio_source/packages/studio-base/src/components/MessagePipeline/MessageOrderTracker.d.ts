import { PlayerState, PlayerProblem } from "@foxglove/studio-base/players/types";
declare class MessageOrderTracker {
    #private;
    update(playerState: PlayerState): PlayerProblem[];
}
export default MessageOrderTracker;
