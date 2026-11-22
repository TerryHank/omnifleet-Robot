// This Source Code Form is subject to the terms of the Mozilla Public
// License, v2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/
import { makePose } from "./transforms";
const tempPose = makePose();
export function updatePose(renderable, transformTree, renderFrameId, fixedFrameId, srcFrameId, dstTime, srcTime) {
    const pose = renderable.userData.pose;
    if (!pose) {
        throw new Error(`Missing userData.pose for ${renderable.name}`);
    }
    const poseApplied = Boolean(transformTree.apply(tempPose, pose, renderFrameId, fixedFrameId, srcFrameId, dstTime, srcTime));
    renderable.visible = poseApplied;
    if (poseApplied) {
        const p = tempPose.position;
        const q = tempPose.orientation;
        renderable.position.set(p.x, p.y, p.z);
        renderable.quaternion.set(q.x, q.y, q.z, q.w);
    }
    return poseApplied;
}
