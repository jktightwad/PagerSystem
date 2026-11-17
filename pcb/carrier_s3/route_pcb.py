"""Routes carrier_s3.kicad_pcb (made by build_pcb.py) with a simple grid A* router,
then adds GND pours and writes a DRC report.

Two layers, 0.1 mm grid, 8 directions, vias between layers. Each net is grown as a
tree: the nearest unconnected pad is joined to everything already routed on that net.
If a net fails, the whole board is re-routed with the failed nets first.

Run with the system python (KiCad's pcbnew) after build_pcb.py:  python3 route_pcb.py
Needs numpy and scipy.
"""
import heapq, math, random, sys
import numpy as np
from scipy.ndimage import distance_transform_edt
import pcbnew

IN = OUT = "carrier_s3.kicad_pcb"
G = 0.1                 # grid, mm
CLR = 0.2               # copper clearance (design rule)
MARGIN = 0.09           # raster error allowance
EDGE_CLR = 0.3
VIA_D, VIA_DRILL = 0.6, 0.3
VIA_COST = 25           # in grid steps
WIDTH = {"VBAT": 0.5, "BAT+": 0.5, "POGO5V": 0.4, "GND": 0.4, "MOT_-": 0.4, "BUZ_-": 0.3, "3V3": 0.3}
SIG_W = 0.25
TOP_KEEPOUT = [(7.65, 0.6, 19.35, 24.6)]   # under the SuperMini body (x0, y0, x1, y1): no top copper
ZONE_NET = "GND"

def mm(v): return pcbnew.FromMM(v)
def to_mm(v): return pcbnew.ToMM(v)


class Router:
    def __init__(self, board):
        self.b = board
        bb = board.GetBoardEdgesBoundingBox()
        self.W, self.H = to_mm(bb.GetRight()) - 0.05, to_mm(bb.GetBottom()) - 0.05   # minus half the edge line
        self.NX, self.NY = int(round(self.W / G)) + 1, int(round(self.H / G)) + 1
        self.cu = np.zeros((2, self.NY, self.NX), np.int32)    # net code per cell, -1 = keepout
        self.padcells = np.zeros((2, self.NY, self.NX), bool)   # any pad copper (no vias near pads)
        self.holes = np.zeros((self.NY, self.NX), bool)
        self.netpads = {}                                       # net name -> list of (cells set)
        self._edges()
        self._pads()
        self._keepouts()

    # ---------- rasterising ----------
    def cell(self, x, y): return int(round(y / G)), int(round(x / G))
    def xy(self, r, c): return c * G, r * G

    def _edges(self):
        rr, cc = np.mgrid[0:self.NY, 0:self.NX]
        x, y = cc * G, rr * G
        R = 1.5
        d = np.minimum(np.minimum(x, self.W - x), np.minimum(y, self.H - y))
        qx = np.maximum(np.maximum(R - x, x - (self.W - R)), 0)
        qy = np.maximum(np.maximum(R - y, y - (self.H - R)), 0)
        corner = (qx > 0) & (qy > 0)
        d = np.where(corner, R - np.hypot(qx, qy), d)
        edge = d < 0.12          # tracks keep CLR + MARGIN from these cells -> >= EDGE_CLR from the edge
        self.cu[0][edge] = -1; self.cu[1][edge] = -1

    def _pads(self):
        for fp in self.b.GetFootprints():
            for pad in fp.Pads():
                bb = pad.GetBoundingBox()
                r0, c0 = self.cell(to_mm(bb.GetLeft()), to_mm(bb.GetTop()))
                r1, c1 = self.cell(to_mm(bb.GetRight()), to_mm(bb.GetBottom()))
                net = pad.GetNetCode()
                lays = [l for l, lid in enumerate((pcbnew.F_Cu, pcbnew.B_Cu)) if pad.IsOnLayer(lid)]
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    lays = [0, 1]; net = -1
                cells = set()
                for r in range(max(r0, 0), min(r1 + 1, self.NY)):
                    for c in range(max(c0, 0), min(c1 + 1, self.NX)):
                        x, y = self.xy(r, c)
                        if pad.HitTest(pcbnew.VECTOR2I(mm(x), mm(y))):
                            for l in lays:
                                self.cu[l, r, c] = net if net > 0 else -1
                                self.padcells[l, r, c] = True
                                cells.add((l, r, c))
                            if pad.GetDrillSize().x > 0:
                                self.holes[r, c] = True
                if net > 0 and cells:
                    self.netpads.setdefault(pad.GetNetname(), []).append((f"{fp.GetReference()}.{pad.GetNumber()}", cells))
            if fp.GetReference().startswith("MH"):       # screw head keepout
                p = fp.GetPosition(); self._disc(to_mm(p.x), to_mm(p.y), 2.0, [0, 1], -1)
                self._disc(to_mm(p.x), to_mm(p.y), 1.1, [0, 1], -1, hole=True)

    def _disc(self, x, y, rad, lays, val, hole=False):
        rr, cc = np.mgrid[0:self.NY, 0:self.NX]
        m = np.hypot(cc * G - x, rr * G - y) <= rad
        for l in lays: self.cu[l][m] = val
        if hole: self.holes[m] = True

    def _keepouts(self):
        for x0, y0, x1, y1 in TOP_KEEPOUT:
            r0, c0 = self.cell(x0, y0); r1, c1 = self.cell(x1, y1)
            blk = self.cu[0, r0:r1 + 1, c0:c1 + 1]
            blk[blk == 0] = -1

    # ---------- routing ----------
    def free_maps(self, code, hw):
        free = []
        for l in range(2):
            foreign = (self.cu[l] != 0) & (self.cu[l] != code)
            d = distance_transform_edt(~foreign) * G
            free.append(d >= hw + CLR + MARGIN)
        anypad = self.padcells[0] | self.padcells[1]
        dpad = distance_transform_edt(~anypad) * G
        dhole = distance_transform_edt(~self.holes) * G
        via_ok = []
        for l in range(2):
            foreign = (self.cu[l] != 0) & (self.cu[l] != code)
            via_ok.append(distance_transform_edt(~foreign) * G >= VIA_D / 2 + CLR + MARGIN)
        vok = via_ok[0] & via_ok[1] & (dpad >= VIA_D / 2 + CLR + MARGIN) & (dhole >= VIA_DRILL / 2 + 0.35)
        return np.stack(free), vok

    def astar(self, starts, targets, free, vok):
        NX, NY = self.NX, self.NY
        N = NX * NY
        fr = free.reshape(-1).tolist(); vk = vok.reshape(-1).tolist()
        tgt = set(l * N + r * NX + c for l, r, c in targets)
        trs = [(r, c) for _, r, c in targets]
        tr0, tr1 = min(t[0] for t in trs), max(t[0] for t in trs)
        tc0, tc1 = min(t[1] for t in trs), max(t[1] for t in trs)
        def h(r, c):
            dr = max(tr0 - r, 0, r - tr1); dc = max(tc0 - c, 0, c - tc1)
            return max(dr, dc) + 0.4142 * min(dr, dc)
        g = {}; came = {}; pq = []
        for l, r, c in starts:
            i = l * N + r * NX + c
            g[i] = 0.0; came[i] = (-1, -1)
            heapq.heappush(pq, (h(r, c), 0.0, i))
        dirs = [(0, 1, 1.0), (1, 0, 1.0), (0, -1, 1.0), (-1, 0, 1.0),
                (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
        while pq:
            f, gc, i = heapq.heappop(pq)
            if gc > g.get(i, 1e18): continue
            if i in tgt:
                path = []
                while i != -1:
                    path.append(i); i = came[i][0]
                return [(p // N, (p % N) // NX, p % NX) for p in reversed(path)]
            l, rem = divmod(i, N); r, c = divmod(rem, NX)
            pdir = came[i][1]
            for k, (dr, dc, cost) in enumerate(dirs):
                rr, cc = r + dr, c + dc
                if not (0 <= rr < NY and 0 <= cc < NX): continue
                j = l * N + rr * NX + cc
                if not fr[j]: continue
                if k >= 4:   # diagonal: both corner cells free too (no squeezing past corners)
                    if not fr[l * N + r * NX + cc] or not fr[l * N + rr * NX + c]: continue
                ng = gc + cost + (0.3 if pdir not in (-1, k) else 0)
                if ng < g.get(j, 1e18):
                    g[j] = ng; came[j] = (i, k); heapq.heappush(pq, (ng + h(rr, cc), ng, j))
            if vk[rem]:
                j = (1 - l) * N + rem
                if fr[j]:
                    ng = gc + VIA_COST
                    if ng < g.get(j, 1e18):
                        g[j] = ng; came[j] = (i, -1); heapq.heappush(pq, (ng + h(r, c), ng, j))
        return None

    def mark_track(self, a, b, l, hw, code):
        (x0, y0), (x1, y1) = a, b
        rr = hw + G * 0.5
        r0, c0 = self.cell(min(x0, x1) - rr, min(y0, y1) - rr)
        r1, c1 = self.cell(max(x0, x1) + rr, max(y0, y1) + rr)
        dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy
        cells = []
        for r in range(max(r0, 0), min(r1 + 1, self.NY)):
            for c in range(max(c0, 0), min(c1 + 1, self.NX)):
                x, y = self.xy(r, c)
                t = 0 if L2 == 0 else max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / L2))
                if math.hypot(x - (x0 + t * dx), y - (y0 + t * dy)) <= hw:
                    if self.cu[l, r, c] == 0: self.cu[l, r, c] = code
                    cells.append((l, r, c))
        return cells

    def commit(self, path, net, hw):
        """path -> tracks / vias on the board; returns the new copper cells"""
        code = net.GetNetCode(); cells = []
        lay = (pcbnew.F_Cu, pcbnew.B_Cu)
        # split into same-layer runs
        runs = []; cur = [path[0]]
        for p in path[1:]:
            if p[0] != cur[-1][0]:
                runs.append(cur); cur = [p]
            else: cur.append(p)
        runs.append(cur)
        for k, run in enumerate(runs):
            pts = [self.xy(r, c) for _, r, c in run]
            # merge collinear steps
            corners = [pts[0]]
            for i in range(1, len(pts) - 1):
                d1 = (round((pts[i][0] - pts[i-1][0]) / G), round((pts[i][1] - pts[i-1][1]) / G))
                d2 = (round((pts[i+1][0] - pts[i][0]) / G), round((pts[i+1][1] - pts[i][1]) / G))
                if d1 != d2: corners.append(pts[i])
            if len(pts) > 1: corners.append(pts[-1])
            l = run[0][0]
            for a, b in zip(corners, corners[1:]):
                t = pcbnew.PCB_TRACK(self.b); t.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
                t.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1]))); t.SetWidth(mm(2 * hw)); t.SetLayer(lay[l])
                t.SetNet(net); self.b.Add(t)
                cells += self.mark_track(a, b, l, hw, code)
            if len(corners) == 1:
                cells += self.mark_track(corners[0], corners[0], l, hw, code)
            if k < len(runs) - 1:
                x, y = pts[-1]
                v = pcbnew.PCB_VIA(self.b); v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL)); v.SetNet(net); self.b.Add(v)
                r, c = self.cell(x, y)
                for l2 in (0, 1): cells += self.mark_track((x, y), (x, y), l2, VIA_D / 2, code)
                self.holes[r, c] = True
        return cells

    def route_net(self, name):
        net = self.b.FindNet(name); code = net.GetNetCode()
        hw = WIDTH.get(name, SIG_W) / 2
        pads = list(self.netpads.get(name, []))
        if len(pads) < 2: return True
        free, vok = self.free_maps(code, hw)
        # own pad cells are always enterable
        tree = set(pads[0][1]); todo = pads[1:]
        while todo:
            # nearest pad to the tree (centre distance)
            tr = np.array([(r, c) for _, r, c in tree])
            def dist(p):
                pr = np.array([(r, c) for _, r, c in p[1]]).mean(0)
                return np.min(np.abs(tr - pr).sum(1))
            todo.sort(key=dist)
            ref, cells = todo.pop(0)
            for l, r, c in cells | tree: free[l, r, c] = True
            path = self.astar(tree, cells, free, vok)
            if path is None:
                print(f"  {name}: no path to {ref}"); return False
            new = self.commit(path, net, hw)
            tree |= cells | set(new)
            free, vok = self.free_maps(code, hw)
        return True


def run(order):
    board = pcbnew.LoadBoard(IN)
    for t in list(board.GetTracks()): board.Remove(t)
    for z in list(board.Zones()):
        if not z.GetIsRuleArea(): board.Remove(z)
    rt = Router(board)
    failed = [n for n in order if not rt.route_net(n)]
    return board, failed


def add_zones(board):
    net = board.FindNet(ZONE_NET)
    bb = board.GetBoardEdgesBoundingBox()
    for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board); z.SetLayer(lay); z.SetNet(net)
        z.SetLocalClearance(mm(0.25)); z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline(); ol.NewOutline()
        for x, y in [(bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
                     (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())]:
            ol.Append(x, y)
        board.Add(z)
    # no top pour under the SuperMini
    for x0, y0, x1, y1 in TOP_KEEPOUT:
        k = pcbnew.ZONE(board); k.SetIsRuleArea(True); k.SetDoNotAllowCopperPour(True)
        k.SetDoNotAllowTracks(False); k.SetDoNotAllowVias(False); k.SetDoNotAllowPads(False)
        k.SetDoNotAllowFootprints(False); k.SetLayer(pcbnew.F_Cu)
        ol = k.Outline(); ol.NewOutline()
        for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]: ol.Append(mm(x), mm(y))
        board.Add(k)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


if __name__ == "__main__":
    b0 = pcbnew.LoadBoard(IN)
    names = [n for n in b0.GetNetsByName().keys() if str(n)]
    names = [str(n) for n in names]
    # short / signal nets first, wide power next, GND last
    order = sorted(names, key=lambda n: (n == "GND", n in WIDTH, n))
    random.seed(1)
    for attempt in range(40):
        print(f"attempt {attempt + 1}: {' '.join(order)}")
        board, failed = run(order)
        if not failed: break
        rest = [n for n in order if n not in failed]
        random.shuffle(rest)
        order = failed + rest
    else:
        print("could not route:", failed); board.Save(OUT); sys.exit(1)
    add_zones(board)
    board.Save(OUT)
    pcbnew.WriteDRCReport(board, "drc_report.txt", pcbnew.EDA_UNITS_MILLIMETRES, True)
    print("routed and saved", OUT, "- DRC report in drc_report.txt")
