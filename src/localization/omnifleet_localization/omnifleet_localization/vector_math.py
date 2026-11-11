"""Small frame-conversion helpers used by navigation mapping utilities."""

import math


def normalize_quaternion(quaternion):
    x, y, z, w = (float(value) for value in quaternion)
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm <= 1.0e-12:
        raise ValueError("quaternion has zero length")
    return (x / norm, y / norm, z / norm, w / norm)


def rotate_vector_inverse(vector, quaternion):
    """Rotate a vector from the quaternion parent frame into its child frame."""
    x, y, z, w = normalize_quaternion(quaternion)
    vx, vy, vz = (float(value) for value in vector)
    # Conjugate(q) * v * q, expanded to avoid a geometry dependency in tests.
    tx = 2.0 * (-y * vz + z * vy)
    ty = 2.0 * (-z * vx + x * vz)
    tz = 2.0 * (-x * vy + y * vx)
    return (
        vx + w * tx + (-y * tz + z * ty),
        vy + w * ty + (-z * tx + x * tz),
        vz + w * tz + (-x * ty + y * tx),
    )
