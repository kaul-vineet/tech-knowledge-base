"""L100 agent-based model: Schelling's neighbourhood model on a 30x30 grid (numpy only).

Each agent (type 1 or 2) is happy if at least WANT of its occupied neighbours are its own type.
Unhappy agents move to a random empty cell. Watch "% similar neighbours" rise far above WANT.

python schelling.py
"""
import numpy as np

SIZE, EMPTY_FRAC, WANT = 30, 0.10, 0.30  # 30% similar wanted, like NetLogo's default slider example


def make_grid(rng):
    cells = SIZE * SIZE
    n_empty = int(cells * EMPTY_FRAC)
    n_each = (cells - n_empty) // 2
    flat = np.array([0] * (cells - 2 * n_each) + [1] * n_each + [2] * n_each)
    rng.shuffle(flat)  # agents start randomly mixed
    return flat.reshape(SIZE, SIZE)


def neighbour_counts(grid, kind):
    # count same-kind neighbours in the 8-cell Moore neighbourhood; np.roll wraps edges (torus, like NetLogo)
    mask = (grid == kind).astype(int)
    return sum(np.roll(np.roll(mask, dy, 0), dx, 1)
               for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy, dx) != (0, 0))


def similarity(grid):
    same = np.where(grid == 1, neighbour_counts(grid, 1), neighbour_counts(grid, 2))
    occupied = neighbour_counts(grid, 1) + neighbour_counts(grid, 2)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(occupied > 0, same / occupied, 1.0)  # no neighbours -> treated as happy
    return np.where(grid > 0, frac, np.nan)


def step(grid, rng):
    frac = similarity(grid)
    unhappy = np.argwhere(frac < WANT)  # agent rule: local, simple, no global plan
    rng.shuffle(unhappy)  # random activation order
    for y, x in unhappy:
        empties = np.argwhere(grid == 0)
        ey, ex = empties[rng.integers(len(empties))]
        grid[ey, ex], grid[y, x] = grid[y, x], 0  # move to a random empty cell
    return len(unhappy)


def stats(grid):
    frac = similarity(grid)
    agents = ~np.isnan(frac)
    return 100 * np.nanmean(frac), 100 * (frac[agents] < WANT).mean()


def run(seed=42, max_steps=50, verbose=False):
    rng = np.random.default_rng(seed)  # one seeded generator drives setup AND moves
    grid = make_grid(rng)
    history = [stats(grid)]
    for i in range(1, max_steps + 1):
        moved = step(grid, rng)
        history.append(stats(grid))
        if verbose and (i <= 3 or i % 5 == 0 or history[-1][1] == 0):
            print(f"step {i:2}: moved {moved:3}  % similar {history[-1][0]:5.1f}  % unhappy {history[-1][1]:5.1f}")
        if history[-1][1] == 0:  # stop when everyone is happy
            break
    return grid, history


def main():
    grid, history = run(verbose=True)
    print(f"start: % similar {history[0][0]:.1f} -> end: {history[-1][0]:.1f} (each agent only wanted {100 * WANT:.0f}%)")
    print("top-left 10x10 corner at the end (. empty, x / o agent types):")
    for row in grid[:10, :10]:
        print(" ".join(".xo"[c] for c in row))


if __name__ == "__main__":
    main()
