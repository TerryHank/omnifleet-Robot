"""Small, ROS-independent occupancy evidence model used by GLIM map projection."""

from collections import deque


class OccupancyEvidence:
    """Confirm occupied cells with bounded K/N histories.

    Neighboring observations contribute temporal support but retain their own
    coordinates.  This avoids collapsing a continuous wall into isolated
    canonical cells while still tolerating one-cell registration jitter.
    """

    def __init__(
        self,
        hit_threshold=5,
        hit_window_size=10,
        strong_hit_threshold=3,
        strong_hit_window_size=4,
        persistent_hit_threshold=8,
        persistent_hit_window_size=12,
        miss_threshold=3,
        candidate_ttl=2.0,
        free_threshold=3,
        free_candidate_ttl=2.0,
        hit_tolerance_cells=1,
    ):
        self.hit_threshold = max(1, int(hit_threshold))
        self.hit_window_size = max(self.hit_threshold, int(hit_window_size))
        self.strong_hit_threshold = max(1, int(strong_hit_threshold))
        self.strong_hit_window_size = max(
            self.strong_hit_threshold, int(strong_hit_window_size)
        )
        self.persistent_hit_threshold = max(1, int(persistent_hit_threshold))
        self.persistent_hit_window_size = max(
            self.persistent_hit_threshold, int(persistent_hit_window_size)
        )
        self.miss_threshold = max(1, int(miss_threshold))
        self.candidate_ttl = max(0.1, float(candidate_ttl))
        self.free_threshold = max(1, int(free_threshold))
        self.free_candidate_ttl = max(0.1, float(free_candidate_ttl))
        self.hit_tolerance_cells = max(0, int(hit_tolerance_cells))
        self.last_hits = {}
        self.miss_counts = {}
        self.free_counts = {}
        self.last_free = {}
        self.confirmed = set()
        self.known_free = set()
        history_size = max(
            self.hit_window_size,
            self.strong_hit_window_size,
            self.persistent_hit_window_size,
        )
        self.hit_history = deque(maxlen=history_size)
        self.quality_history = deque(maxlen=history_size)
        self.strong_history = deque(maxlen=history_size)
        self.current_time = 0.0

    @property
    def has_data(self):
        return bool(
            self.hit_history
            or self.free_counts
            or self.confirmed
            or self.known_free
        )

    @property
    def candidates(self):
        recent = set()
        for timestamp, cells in self.hit_history:
            if self.current_time - timestamp <= self.candidate_ttl:
                recent.update(cells)
        return recent - self.confirmed

    @property
    def free_candidates(self):
        return set(self.free_counts) - self.known_free

    def active_wall_guards(self, now, timeout):
        """Return only recently re-observed confirmed walls for ray blocking."""
        now = float(now)
        timeout = max(0.0, float(timeout))
        return {
            cell
            for cell in self.confirmed
            if now - self.last_hits.get(cell, float("-inf")) <= timeout
        }

    def seed_confirmed(self, occupied_cells, free_cells=(), now=0.0):
        """Bootstrap a saved/global GLIM map without waiting for live scans."""
        now = float(now)
        occupied = set(occupied_cells)
        free = set(free_cells) - occupied
        self.confirmed.update(occupied)
        self.known_free.update(free)
        for cell in occupied:
            self.last_hits[cell] = now
            self.miss_counts[cell] = 0
            self.free_counts.pop(cell, None)
            self.last_free.pop(cell, None)
        for cell in free:
            self.free_counts[cell] = self.free_threshold
            self.last_free[cell] = now

    def _neighbors(self, cell):
        radius = self.hit_tolerance_cells
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                yield (cell[0] + dx, cell[1] + dy)

    def _history_support(self, neighbors, history, window_size):
        support = 0
        for _, cells in list(history)[-window_size:]:
            if neighbors.intersection(cells):
                support += 1
        return support

    def _supported(self, cell):
        neighbors = set(self._neighbors(cell))
        return (
            self._history_support(
                neighbors, self.strong_history, self.strong_hit_window_size
            )
            >= self.strong_hit_threshold
            or self._history_support(
                neighbors, self.quality_history, self.hit_window_size
            )
            >= self.hit_threshold
            or self._history_support(
                neighbors, self.hit_history, self.persistent_hit_window_size
            )
            >= self.persistent_hit_threshold
        )

    def observe(
        self,
        occupied_cells,
        free_cells,
        now,
        strong_cells=None,
        quality_cells=None,
    ):
        """Apply one independent accumulated scan window."""
        now = float(now)
        self.current_time = now
        occupied_observations = set(occupied_cells)
        strong = set(strong_cells or ()) & occupied_observations
        quality = (
            occupied_observations
            if quality_cells is None
            else set(quality_cells) & occupied_observations
        )
        self.hit_history.append((now, occupied_observations))
        self.strong_history.append((now, strong))
        self.quality_history.append((now, quality))

        for confirmed_cell in tuple(self.confirmed):
            if any(cell in occupied_observations for cell in self._neighbors(confirmed_cell)):
                self.last_hits[confirmed_cell] = now
                self.miss_counts[confirmed_cell] = 0

        newly_confirmed = set()
        for observed_cell in occupied_observations:
            if not self._supported(observed_cell):
                continue
            newly_confirmed.add(observed_cell)
            observed_neighbors = set(self._neighbors(observed_cell))
            # Preserve every recently observed coordinate near the supported
            # endpoint; do not collapse adjacent wall cells to one old cell.
            for timestamp, recent_cells in self.hit_history:
                if now - timestamp > self.candidate_ttl:
                    continue
                # Intersect the nine-cell neighborhood directly.  The former
                # generator rebuilt that neighborhood once for every cell in
                # every history window, creating an accidental quadratic loop.
                newly_confirmed.update(observed_neighbors.intersection(recent_cells))

        for cell in newly_confirmed:
            self.confirmed.add(cell)
            self.last_hits[cell] = now
            self.miss_counts[cell] = 0
            self.known_free.discard(cell)
            self.free_counts.pop(cell, None)
            self.last_free.pop(cell, None)

        free = set(free_cells) - occupied_observations
        for cell in free:
            previous = self.last_free.get(cell)
            if previous is None or now - previous > self.free_candidate_ttl:
                self.free_counts[cell] = 1
            else:
                self.free_counts[cell] = self.free_counts.get(cell, 0) + 1
            self.last_free[cell] = now

            if cell in self.confirmed:
                misses = self.miss_counts.get(cell, 0) + 1
                self.miss_counts[cell] = misses
                if misses >= self.miss_threshold:
                    self.confirmed.discard(cell)
                    self.last_hits.pop(cell, None)
                    self.miss_counts.pop(cell, None)

            if (
                self.free_counts[cell] >= self.free_threshold
                and cell not in self.confirmed
            ):
                self.known_free.add(cell)

        stale_free = [
            cell
            for cell, last_seen in self.last_free.items()
            if cell not in self.known_free
            and now - last_seen > self.free_candidate_ttl
        ]
        for cell in stale_free:
            self.free_counts.pop(cell, None)
            self.last_free.pop(cell, None)


def bresenham_free_cells(start, end):
    """Return 2D grid cells traversed before an endpoint."""
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    cells = []
    while (x0, y0) != (x1, y1):
        cells.append((x0, y0))
        doubled = 2 * error
        if doubled >= dy:
            error += dy
            x0 += sx
        if doubled <= dx:
            error += dx
            y0 += sy
    return cells
