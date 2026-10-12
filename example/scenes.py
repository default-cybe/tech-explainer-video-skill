from manim import *
from theme3 import (Base, S, M, mline, dotcube, dotcyl, dotsphere, spin, card, chip, status,
                    avatar, node, toggle, mode_cells, BLACK,INK,DIM,FAINT,LINE,CARD,BLUE,GREEN,RED,AMBER)

class P1_WhatIs(Base):
    KEY="P1_WhatIs"; NUM="02"; TITLE="the runtime"
    def construct(self):
        self.add(self.head())
        title=self.big_title("Untrusted guest, trusted host")
        self.play(FadeIn(title,shift=DOWN*0.2),run_time=0.6)

        # persistent stage: guest cube (left) --copy node-- host card (right)
        cube=dotcube(5,0.26,INK); spin(cube,0.25)
        cube.scale(1.1).move_to(LEFT*4.2+UP*0.1)
        glabel=M("guest · Linux image",17,DIM).next_to(cube,DOWN,buff=0.5)
        self.play(LaggedStart(*[FadeIn(d,scale=0.5) for d in cube],lag_ratio=0.004),run_time=1.2)
        self.play(FadeIn(glabel),run_time=0.4)
        s=self.show_status("a container is an untrusted Linux image")

        hostbody=VGroup(M("~/out",18,INK),M("your files",14,FAINT)).arrange(DOWN,buff=0.12,aligned_edge=LEFT)
        host=card("your Mac","the host",hostbody,w=4.0,h=2.1,accent=False).move_to(RIGHT*4.0+UP*0.1)
        self.play(FadeIn(host,shift=LEFT*0.3),run_time=0.6)
        s=self.show_status("your Mac is the host - this is what you protect", old=s)

        cp=node("copy","container cp",INK,0.34).move_to(UP*0.1)
        l1=DashedLine(cube.get_right(),cp[0].get_left(),color=LINE,stroke_width=1.5)
        l2=DashedLine(cp[0].get_right(),host.get_left(),color=LINE,stroke_width=1.5)
        self.sfx("tick"); self.play(Create(l1),Create(l2),FadeIn(cp),run_time=0.8)

        un=chip("untrusted",danger=True).next_to(glabel,DOWN,buff=0.3)
        tr=chip("trusted",True); tr.next_to(host,DOWN,buff=0.4)
        self.sfx("tick"); self.play(FadeIn(un,scale=0.9),run_time=0.4)
        self.sfx("tick"); self.play(FadeIn(tr,scale=0.9),run_time=0.4)
        s=self.show_status("copying files out crosses that line", BLUE, old=s)
        self.glow(cp,BLUE,0.8,1.4)
        self.finish()


class P2_Undo(Base):
    KEY="P2_Undo"; NUM="06"; TITLE="the bug"
    def construct(self):
        self.add(self.head())
        title=self.big_title("The mask, undone")
        self.play(FadeIn(title,shift=DOWN*0.2),run_time=0.5)

        cells=mode_cells("0o4755",0.66).move_to(UP*1.2)
        req=M("requested mode",16,DIM).next_to(cells,UP,buff=0.3)
        self.play(FadeIn(req),LaggedStart(*[FadeIn(c,scale=0.6) for c in cells],lag_ratio=0.08),run_time=1.0)
        s=self.show_status("the extractor masks the mode when it creates the file")

        # mask gate sweeps; the set-uid '4' (index 2) drops out -> 0755 safe
        gate=VGroup(Line(UP*0.6,DOWN*0.6,color=BLUE,stroke_width=5),M("& 0o777",18,BLUE).shift(DOWN*0.95))
        gate.next_to(cells,LEFT,buff=0.5)
        self.sfx("tick"); self.play(FadeIn(gate,shift=RIGHT*0.2),run_time=0.3)
        self.play(gate.animate.next_to(cells,RIGHT,buff=0.5),run_time=1.1,rate_func=linear)
        self.sfx("pop"); self.play(cells[2].animate.set_opacity(0.12),
                                   cells[2][1].animate.set_color(FAINT),run_time=0.5)
        # file card created SAFE
        fbody=VGroup(mline([("mode  ",DIM),("0755",GREEN)],20),M("set-uid: off",14,FAINT)
                     ).arrange(DOWN,buff=0.14,aligned_edge=LEFT)
        fcard=card("./out/x","created",fbody,w=4.1,h=1.9).move_to(LEFT*3.9+DOWN*1.15)
        self.sfx("tick"); self.play(FadeIn(fcard,shift=UP*0.2),FadeOut(gate),run_time=0.7)
        s=self.show_status("masked to 0755 - safe, no set-UID bit", GREEN, old=s)

        # the undo: fchmod with full mode -> '4' returns, red
        cmt=M("// one line later",16,DIM).move_to(RIGHT*1.4+UP*0.5)
        code=mline([("fchmod",RED),("(fd, ",INK),("entry.permissions",RED),(")",INK)],26)
        code.move_to(RIGHT*1.4+DOWN*0.1)
        self.sfx("tick"); self.play(FadeIn(cmt),Write(code),run_time=0.9)
        self.sfx("pop"); self.play(cells[2].animate.set_opacity(1),cells[2][1].animate.set_color(INK),run_time=0.4)
        self.play(cells[2][0].animate.set_stroke(RED),cells[2][1].animate.set_color(RED),run_time=0.3)
        # file card flips to unsafe
        fbody2=VGroup(mline([("mode  ",DIM),("4755",RED)],20),M("set-uid: ON",14,RED)
                      ).arrange(DOWN,buff=0.14,aligned_edge=LEFT)
        fcard2=card("./out/x","re-applied",fbody2,w=4.1,h=1.9).move_to(LEFT*3.9+DOWN*1.15)
        self.sfx("impact"); self.play(FadeOut(fcard),FadeIn(fcard2),run_time=0.5)
        s=self.show_status("fchmod re-applies the full mode - set-UID is back", RED, old=s)
        self.glow(cells[2],RED,0.8,1.5); self.glow(fcard2,RED,0.8,1.3)
        self.finish()
