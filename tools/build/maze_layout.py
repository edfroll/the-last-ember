"""T-024: the plan of the Enchanted Maze (no world access): the 5x5 cells of 24x24, their inner corridors, the 6 movable cells in
3 variants, the dead ends, the check of all 3^6 = 729 combinations of the movable cells.

Cell (cx, cz): cx 0..4 west -> east, cz 0..4 north -> south. Inside a cell 5 x 5 nodes on 5 lanes (local offsets and widths
LANES: 2, 3, 4, 3, 2 blocks wide, hedges 2 thick between them, the border ring of the cell 1 thick: two cells share a hedge of 2).
A node is a square lane x lane, a link joins two neighbouring nodes through the 2-thick hedge between them (open = path, closed =
hedge). The ports: the middle of every side (node (2,0) N, (4,2) E, (2,4) S, (0,2) W), 3 wide (local 11..13) through the border.
Every node of a cell belongs to one tree of open links, every tree holds at least one port: a cell has no closed pockets.
The secret exit: the middle lane of the cells (2,1) and (2,0) is the corridor from the sanctum to the north edge (filled with hedge
until the key is taken); those two cells are two halves (lanes 0-1 and 3-4) with one port each (W / E)."""
import itertools, random
from collections import deque

LANES = [(1, 2), (5, 3), (10, 4), (16, 3), (21, 2)]      # (local offset, width)
PORT = (11, 13)                                          # local span of every port (3 wide, inside the middle lane 10..13)
N_, E_, S_, W_ = "N", "E", "S", "W"
PORT_NODE = {N_: (2, 0), E_: (4, 2), S_: (2, 4), W_: (0, 2)}
DIRS = {N_: (0, -1), E_: (1, 0), S_: (0, 1), W_: (-1, 0)}
OPP = {N_: S_, S_: N_, E_: W_, W_: E_}
SANCTUM = (2, 2)
GATE = (2, 4)
CORRIDOR = [(2, 1), (2, 0)]
MOVABLE = [(1, 1), (3, 1), (1, 3), (3, 3), (0, 2), (4, 2)]

def cell_ports(c):
    """the ports of a cell that belong to the maze graph (outer sides have none; the gate is the S port of (2,4))"""
    cx, cz = c; out = []
    for d, (dx, dz) in DIRS.items():
        nx, nz = cx + dx, cz + dz
        if c in CORRIDOR and d in (N_, S_): continue
        if c == SANCTUM and d == N_: continue
        if not (0 <= nx < 5 and 0 <= nz < 5):
            if c == GATE and d == S_: out.append(d)
            continue
        out.append(d)
    return out

def nodes_of(c):
    if c in CORRIDOR: return [(i, j) for i in (0, 1, 3, 4) for j in range(5)]
    return [(i, j) for i in range(5) for j in range(5)]

def nb(n, allowed):
    i, j = n
    for d, (dx, dz) in DIRS.items():
        q = (i + dx, j + dz)
        if q in allowed: yield q

def link(a, b): return (a, b) if a < b else (b, a)

def grow_cell(c, groups, rnd, tries=400):
    """groups: list of port lists. Returns (links: set of open node pairs, region: node -> group index) or None.
    Each group's region is a tree of open links holding its ports; together the regions cover every node of the cell."""
    allowed = set(nodes_of(c))
    for _ in range(tries):
        reg = {}; ok = True
        order = list(range(len(groups))); rnd.shuffle(order)
        for g in order:
            ps = [PORT_NODE[p] for p in groups[g]]
            other_ports = {PORT_NODE[p] for h, gg in enumerate(groups) if h != g for p in gg}
            reg[ps[0]] = g
            for p in ps[1:]:      # a random path from the region to the next port through free nodes
                free = {n for n in allowed if n not in reg and n not in other_ports} | {p}
                src = [n for n, v in reg.items() if v == g]
                prev = {n: None for n in src}; dq = deque(src); rnd.shuffle(dq)
                while dq:
                    n = dq.popleft()
                    if n == p: break
                    nbs = list(nb(n, free)); rnd.shuffle(nbs)
                    for q in nbs:
                        if q not in prev: prev[q] = n; dq.append(q)
                if p not in prev: ok = False; break
                n = p
                while n is not None and n not in reg: reg[n] = g; n = prev[n]
            if not ok: break
        if not ok: continue
        # every group must still be able to reach its own ports... done; now grow all regions over the free nodes
        free = [n for n in allowed if n not in reg]
        guard = 0
        while free and guard < 500:
            guard += 1; rnd.shuffle(free)
            for n in list(free):
                gs = [reg[q] for q in nb(n, allowed) if q in reg]
                if gs: reg[n] = rnd.choice(gs); free.remove(n)
        if free: continue
        # a spanning tree per region: depth-first (long corridors, few dead ends), from the first port of the group
        links = set()
        for g, gg in enumerate(groups):
            rn = {n for n, v in reg.items() if v == g}
            start = PORT_NODE[gg[0]]; seen = {start}; st = [start]
            while st:
                n = st[-1]; cand = [q for q in nb(n, rn) if q not in seen]
                if not cand: st.pop(); continue
                q = rnd.choice(cand); seen.add(q); links.add(link(n, q)); st.append(q)
            if seen != rn: break
        else:
            return links, reg
    return None

def dead_ends(c, links):
    """leaves of the trees that are not port nodes: (node, exit direction)"""
    ports = {PORT_NODE[p] for p in cell_ports(c)}
    deg = {}
    for a, b in links:
        deg.setdefault(a, []).append(b); deg.setdefault(b, []).append(a)
    out = []
    for n in nodes_of(c):
        if n in ports or len(deg.get(n, [])) != 1: continue
        q = deg[n][0]; d = [k for k, v in DIRS.items() if (n[0] + v[0], n[1] + v[1]) == q][0]
        out.append((n, d))
    return out

def partitions(ports):
    """all set partitions of the ports (as lists of lists)"""
    ports = list(ports)
    if not ports: yield []; return
    first, rest = ports[0], ports[1:]
    for p in partitions(rest):
        for i in range(len(p)): yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p

class Plan:
    """cells: c -> list of variants; a variant = dict(groups, links, region, dead)"""
    def __init__(self, cells): self.cells = cells
    def graph(self, combo):
        """node graph for one combination (dict movable cell -> variant index): nodes (cx, cz, i, j)"""
        adj = {}
        def add(a, b): adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
        for c, vs in self.cells.items():
            v = vs[combo.get(c, 0)]
            for n in nodes_of(c): adj.setdefault((c[0], c[1]) + n, set())
            for a, b in v["links"]: add((c[0], c[1]) + a, (c[0], c[1]) + b)
            for p in cell_ports(c):
                dx, dz = DIRS[p]; o = (c[0] + dx, c[1] + dz)
                if o in self.cells and OPP[p] in cell_ports(o):
                    add((c[0], c[1]) + PORT_NODE[p], (o[0], o[1]) + PORT_NODE[OPP[p]])
        return adj
    def check(self, combo):
        adj = self.graph(combo)
        start = GATE + PORT_NODE[S_]; goal = SANCTUM + (2, 2)
        dist = {start: 0}; dq = deque([start])
        while dq:
            n = dq.popleft()
            for q in adj[n]:
                if q not in dist: dist[q] = dist[n] + 1; dq.append(q)
        unreached = [n for n in adj if n not in dist]
        return dist.get(goal), unreached
    def combos(self):
        for vs in itertools.product(range(3), repeat=len(MOVABLE)): yield dict(zip(MOVABLE, vs))

def sanctum_variant():
    """the sanctum is one open court (all its nodes joined), built by its own code"""
    c = SANCTUM; ns = nodes_of(c); links = set()
    for n in ns:
        for q in nb(n, set(ns)): links.add(link(n, q))
    return dict(groups=[cell_ports(c)], links=links, region={n: 0 for n in ns}, dead=[])

def corridor_variant(c, rnd):
    """the two halves of a corridor cell: west half (lanes 0-1) with the W port, east half (lanes 3-4) with the E port"""
    links = set(); dead = []
    for half, port in (((0, 1), W_), ((3, 4), E_)):
        rn = {(i, j) for i in half for j in range(5)}
        start = PORT_NODE[port]; seen = {start}; st = [start]
        while st:
            n = st[-1]; cand = [q for q in nb(n, rn) if q not in seen]
            if not cand: st.pop(); continue
            q = rnd.choice(cand); seen.add(q); links.add(link(n, q)); st.append(q)
    return dict(groups=[[W_], [E_]], links=links, region=None, dead=dead_ends(c, links))

# ---------------------------------------------------------------- macro search (partitions only, then the trees)
def macro_eval(parts, early=False):
    """parts: c -> list of partitions (1 for permanent, 3 for movable). Over all 729 combinations: (bad, min, avg, max) of the
    shortest gate -> sanctum path in cell-groups, bad = combinations with an unreachable group"""
    cells = list(parts); res = []; bad = 0
    for combo in itertools.product(range(3), repeat=len(MOVABLE)):
        cm = dict(zip(MOVABLE, combo)); gid = {}; adj = {}
        for c in cells:
            p = parts[c][cm.get(c, 0)]
            for k, g in enumerate(p):
                for port in g: gid[(c, port)] = (c, k)
                adj.setdefault((c, k), set())
        for (c, port), u in gid.items():
            dx, dz = DIRS[port]; o = (c[0] + dx, c[1] + dz)
            v = gid.get((o, OPP[port]))
            if v: adj[u].add(v); adj[v].add(u)
        start = gid[(GATE, S_)]; goal = (SANCTUM, 0)
        dist = {start: 0}; dq = deque([start])
        while dq:
            n = dq.popleft()
            for q in adj[n]:
                if q not in dist: dist[q] = dist[n] + 1; dq.append(q)
        if len(dist) != len(adj):
            bad += 1; res.append(0)
            if early: return bad, 0, 0, 0
        else: res.append(dist[goal])
    return bad, min(res), sum(res) / len(res), max(res)

def macro_search(seed=1, iters=3000):
    """hill climb over the partitions; only plans where all 729 combinations are fine are kept"""
    rnd = random.Random(seed)
    allp = {}
    for cz in range(5):
        for cx in range(5):
            c = (cx, cz)
            if c == SANCTUM: allp[c] = [[cell_ports(c)]]
            elif c in CORRIDOR: allp[c] = [[[W_], [E_]]]
            else: allp[c] = list(partitions(cell_ports(c)))
    def planar(p): return not (len(p) == 2 and all(len(g) == 2 for g in p) and any(set(g) in ({N_, S_}, {E_, W_}) for g in p))
    def ok_mov(p): return len(p) >= 2 and planar(p)
    def ok_perm(c, p): return planar(p) and not (c == GATE and [S_] in p)
    MOV = {c: [p for p in allp[c] if ok_mov(p) and not (c == (1, 1) and [E_] in p) and not (c == (3, 1) and [W_] in p)] for c in MOVABLE}
    PERM = {c: [p for p in allp[c] if ok_perm(c, p)] for c in allp if c not in MOVABLE and c != SANCTUM and c not in CORRIDOR}
    def score(e): bad, mn, avg, mx = e; return mn * 3 + avg + 0.7 * (mx - mn)
    cur = {c: [[cell_ports(c)]] for c in PERM}; cur[SANCTUM] = allp[SANCTUM]
    for c in CORRIDOR: cur[c] = allp[c]
    while True:
        for c in MOVABLE: cur[c] = rnd.sample(MOV[c], 3)
        ce = macro_eval(cur)
        if ce[0] == 0: break
    best = (score(ce), {k: list(v) for k, v in cur.items()}, ce); T = 2.0
    for it in range(iters):
        nxt = {c: list(v) for c, v in cur.items()}
        for _ in range(rnd.choice((1, 1, 2))):
            c = rnd.choice(list(PERM) + MOVABLE)
            if c in MOVABLE:
                k = rnd.randrange(3); cand = [p for p in MOV[c] if p not in nxt[c]]; nxt[c][k] = rnd.choice(cand)
            else: nxt[c] = [rnd.choice(PERM[c])]
        ne = macro_eval(nxt, True)
        if ne[0]: continue
        T = 2.0 * (1 - it / iters) + 0.05
        if score(ne) >= score(ce) or rnd.random() < pow(2.718, (score(ne) - score(ce)) / T): cur, ce = nxt, ne
        if score(ce) > best[0]: best = (score(ce), {k: list(v) for k, v in cur.items()}, ce)
        if it % 200 == 0: print(it, best[0], best[2], flush=True)
    return best

# ---------------------------------------------------------------- the final plan: partitions (maze_macro.json) -> trees -> maze_plan.json
def build_plan(parts, seed):
    rnd = random.Random(seed); cells = {}
    for c, ps in sorted(parts.items()):
        if c == SANCTUM: cells[c] = [sanctum_variant()]; continue
        if c in CORRIDOR: cells[c] = [corridor_variant(c, rnd)]; continue
        vs = []
        for p in ps:
            r = grow_cell(c, p, rnd)
            if r is None: return None
            links = braid(c, r[0], r[1], rnd)
            vs.append(dict(groups=p, links=links, region=r[1], dead=dead_ends(c, links)))
        cells[c] = vs
    return Plan(cells)

BRAID = 0.5
def braid(c, links, region, rnd):
    """half of the dead ends get a second opening into a neighbour node of the same tree (a loop inside the region: fewer dead
    ends, the regions and so the ports they join stay the same)"""
    links = set(links)
    for n, d in dead_ends(c, links):
        if rnd.random() >= BRAID: continue
        cand = [q for q in nb(n, set(nodes_of(c))) if region.get(q) == region.get(n) and link(n, q) not in links]
        if cand: links.add(link(n, rnd.choice(cand)))
    return links

def node_eval(plan):
    ds = []; bad = []
    for combo in plan.combos():
        d, un = plan.check(combo)
        if d is None or un: bad.append(combo)
        ds.append(d or 0)
    return bad, min(ds), sum(ds) / len(ds), max(ds)

def load_macro(path):
    import json, ast
    d = json.load(open(path)); return {ast.literal_eval(k): v for k, v in d.items()}

if __name__ == "__main__" and len(__import__("sys").argv) > 1 and __import__("sys").argv[1] == "plan":
    import json, os, sys
    here = os.path.dirname(os.path.abspath(__file__))
    parts = load_macro(os.path.join(here, "maze_macro.json"))
    best = None
    for seed in range(int(sys.argv[2]) if len(sys.argv) > 2 else 40):
        p = build_plan(parts, 2400 + seed)
        if p is None: continue
        bad, mn, avg, mx = node_eval(p)
        nd = sum(len(v["dead"]) for vs in p.cells.values() for v in vs)
        sc = mn + 0.5 * avg - 0.4 * nd
        print(seed, len(bad), mn, round(avg, 1), mx, "dead", nd, flush=True)
        if not bad and (best is None or sc > best[0]): best = (sc, 2400 + seed, mn, avg, mx, nd)
    print("BEST", best)

def write_plan(seed, path):
    import json, os
    here = os.path.dirname(os.path.abspath(__file__))
    p = build_plan(load_macro(os.path.join(here, "maze_macro.json")), seed)
    bad, mn, avg, mx = node_eval(p); assert not bad
    out = {"seed": seed, "check": {"combinations": 729, "bad": 0, "min": mn, "avg": round(avg, 2), "max": mx}, "cells": {}}
    for c, vs in sorted(p.cells.items()):
        out["cells"]["%d,%d" % c] = [dict(groups=v["groups"], links=sorted([list(a) + list(b) for a, b in v["links"]]),
                                          dead=[[n[0], n[1], d] for n, d in v["dead"]]) for v in vs]
    json.dump(out, open(path, "w"), indent=0)
    return out
