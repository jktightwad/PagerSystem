"""Moves the anchor of hand-built footprints (built with absolute pad positions, anchor at 0,0)
to the centre of their pads, without moving any copper or outline. JLCPCB places parts at the
footprint anchor, so this matters for every part it fits (BZ1, and J1/J2/SW1 on the variant).

    python3 fix_anchors.py board.kicad_pcb      (also called from build_main.py)
"""
import sys
import pcbnew

def center_anchors(board):
    """for footprints at (0,0) with unrotated, absolutely placed items: put the anchor at the pad centre
    and re-express every pad / graphic / text relative to it, so nothing moves on the board"""
    moved = []
    for fp in board.GetFootprints():
        pads = list(fp.Pads())
        if not pads or fp.GetPosition() != pcbnew.VECTOR2I(0, 0) or fp.GetOrientationDegrees() != 0:
            continue
        bb = pads[0].GetBoundingBox()
        for p in pads[1:]: bb.Merge(p.GetBoundingBox())
        c = bb.GetCenter()
        pad_abs = [(p, pcbnew.VECTOR2I(p.GetPosition())) for p in pads]
        gfx = []
        for g in fp.GraphicalItems():
            if isinstance(g, pcbnew.FP_SHAPE):
                gfx.append((g, pcbnew.VECTOR2I(g.GetStart()), pcbnew.VECTOR2I(g.GetEnd()), pcbnew.VECTOR2I(g.GetCenter()) if g.GetShape() in (pcbnew.SHAPE_T_CIRCLE, pcbnew.SHAPE_T_ARC) else None))
        fp.SetPosition(c)                      # moves everything by +c ...
        for p, a_ in pad_abs:                  # ... so put each item back where it was
            p.SetPosition(a_); p.SetPos0(pcbnew.VECTOR2I(a_.x - c.x, a_.y - c.y))
        for g, s0, e0, c0 in gfx:
            g.SetStart(s0); g.SetEnd(e0)
            g.SetStart0(pcbnew.VECTOR2I(s0.x - c.x, s0.y - c.y)); g.SetEnd0(pcbnew.VECTOR2I(e0.x - c.x, e0.y - c.y))
        moved.append(fp.GetReference())
    return moved

if __name__ == "__main__":
    b = pcbnew.LoadBoard(sys.argv[1])
    moved = center_anchors(b)
    b.Save(sys.argv[1])
    print("anchors centred:", " ".join(sorted(moved)))
