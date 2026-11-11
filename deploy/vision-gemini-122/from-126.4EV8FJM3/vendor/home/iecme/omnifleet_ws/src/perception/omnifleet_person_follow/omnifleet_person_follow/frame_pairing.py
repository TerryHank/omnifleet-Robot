"""Pair independent RGB/depth clocks without making RGB wait for depth."""


def pop_frame_pair(frames, depths, key, tolerance_ns=0):
    stamp = lambda value: value[0]*1_000_000_000 + value[1]
    if key in frames:
        rgb_key = key
        if not depths:
            return None
        depth_key = min(depths, key=lambda value: abs(stamp(value)-stamp(rgb_key)))
    elif key in depths:
        depth_key = key
        if not frames:
            return None
        rgb_key = min(frames, key=lambda value: abs(stamp(value)-stamp(depth_key)))
    else:
        return None
    delta = stamp(depth_key)-stamp(rgb_key)
    if abs(delta) > tolerance_ns:
        return None
    return rgb_key, frames.pop(rgb_key), depths.pop(depth_key), delta/1_000_000
