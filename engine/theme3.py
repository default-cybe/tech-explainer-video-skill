"""ED-style engine: pure black, monochrome + one blue accent, macOS cards,
dotted point-cloud objects, persistent-stage diagrams, bottom status pill, calm motion."""
import json, os, math, numpy as np
from manim import *

BLACK="#000000"; INK="#f2f2f2"; DIM="#8a8a8a"; FAINT="#555555"
LINE="#2a2a2a"; CARD="#111216"; CARD2="#17181d"
# higher-luma, lower-saturation accents (GitHub on-dark) - avoid 4:2:0 chroma speckle on black
BLUE="#539bf5"; GREEN="#56d364"; RED="#ff7b72"; AMBER="#e3b341"
SANS="Noto Sans"; MONO="JetBrains Mono"
config.background_color=BLACK

_DUR={}
try: _DUR=json.load(open(os.path.join(os.path.dirname(__file__),"audio","durations.json")))
except Exception: pass

def S(t,s=32,c=INK,w=NORMAL,**k): return Text(t,font=SANS,font_size=s,color=c,weight=w,**k)
def M(t,s=24,c=DIM,**k): return Text(t,font=MONO,font_size=s,color=c,**k)

def mline(parts,s=28):
    g=VGroup(*[Text(t.replace(" "," "),font=MONO,font_size=s,color=c) for t,c in parts])
    return g.arrange(RIGHT,buff=0.0,aligned_edge=DOWN)

# ---- dotted point-cloud objects (the ED infra motif) ----
def _iso(x,y,z,sc):
    a=math.radians(30)
    return np.array([(x-z)*math.cos(a), (x+z)*math.sin(a)-y, 0])*sc

def dotcube(k=5, sc=0.26, color=INK, r=0.022):
    pts=VGroup()
    for x in range(k):
        for y in range(k):
            for z in range(k):
                if x in(0,k-1) or y in(0,k-1) or z in(0,k-1):  # shell only
                    pts.add(Dot(_iso(x-k/2,y-k/2,z-k/2,sc),radius=r,color=color,fill_opacity=0.85))
    return pts.move_to(ORIGIN)

def dotcyl(rings=5, nper=26, rad=0.95, hstep=0.3, color=INK, r=0.02):
    g=VGroup()
    for ri in range(rings):
        yy=-(ri-rings/2)*hstep
        for i in range(nper):
            th=2*math.pi*i/nper
            g.add(Dot([rad*math.cos(th),yy+0.18*math.sin(th),0],radius=r,color=color,fill_opacity=0.8))
    return g.move_to(ORIGIN)

def dotsphere(n=220, rad=1.0, color=INK, r=0.02):
    g=VGroup(); ga=math.pi*(3-math.sqrt(5))
    for i in range(n):
        y=1-2*(i+0.5)/n; rr=math.sqrt(1-y*y); th=ga*i
        g.add(Dot([rad*rr*math.cos(th), rad*y, 0],radius=r,color=color,
                  fill_opacity=0.5+0.5*abs(math.cos(th))))
    return g.move_to(ORIGIN)

def spin(m, speed=0.25):
    m.add_updater(lambda x,dt: x.rotate(speed*dt))
    return m

# ---- UI cards (macOS window feel) ----
def card(title, subtitle=None, body=None, w=5.2, h=None, accent=False, icon=True):
    body_h=body.height if body is not None else 0.0
    H=h or (1.25+body_h+0.35)
    box=RoundedRectangle(corner_radius=0.14,width=w,height=H,stroke_color=LINE,stroke_width=1.5,
                         fill_color=CARD,fill_opacity=1)
    top=box.get_top()[1]; left=box.get_left()[0]; right=box.get_right()[0]
    hdr=VGroup()
    if icon:
        ic=RoundedRectangle(corner_radius=0.06,width=0.4,height=0.4,stroke_width=0,
                            fill_color=(BLUE if accent else "#2a2c33"),fill_opacity=1)
        hdr.add(VGroup(ic,Dot(radius=0.06,color=INK).move_to(ic)))
    hdr.add(S(title,20,INK,w=BOLD)); hdr.arrange(RIGHT,buff=0.22)
    hdr.move_to([left+0.32+hdr.width/2, top-0.42, 0])
    parts=VGroup(box,hdr)
    if subtitle:
        sub=M(subtitle,15,DIM); sub.move_to([right-0.32-sub.width/2, top-0.42, 0]); parts.add(sub)
    div=Line([left,top-0.78,0],[right,top-0.78,0],color=LINE,stroke_width=1); parts.add(div)
    if body is not None:
        body.move_to([left+0.35+body.width/2, top-0.78-0.28-body_h/2, 0]); parts.add(body)
    return parts

def chip(text, accent=False, danger=False):
    col = INK if accent else (RED if danger else DIM)
    fill = BLUE if accent else "#141519"
    stroke = BLUE if accent else (RED if danger else LINE)
    t=M(text,16,col)
    r=RoundedRectangle(corner_radius=0.16,width=t.width+0.45,height=0.42,
                       stroke_color=stroke,stroke_width=1.3,fill_color=fill,fill_opacity=1)
    return VGroup(r,t)

def status(text, color=INK):
    t=M(text,19,color); dot=Dot(radius=0.05,color=BLUE)
    g=VGroup(dot,t).arrange(RIGHT,buff=0.22)
    r=RoundedRectangle(corner_radius=0.24,width=g.width+0.6,height=0.6,stroke_color=LINE,
                       stroke_width=1.2,fill_color="#0e0f12",fill_opacity=1)
    g.move_to(r)
    return VGroup(r,g)

def avatar(label, color=BLUE):
    ic=RoundedRectangle(corner_radius=0.08,width=0.5,height=0.5,stroke_width=0,fill_color=color,fill_opacity=1)
    head=Circle(radius=0.08,color=INK,fill_opacity=1,stroke_width=0).move_to(ic).shift(UP*0.08)
    body=Arc(radius=0.14,start_angle=PI,angle=PI,color=INK,stroke_width=0).move_to(ic).shift(DOWN*0.08)
    bd=AnnularSector(inner_radius=0.0,outer_radius=0.15,angle=PI,start_angle=PI,color=INK).move_to(ic).shift(DOWN*0.1)
    t=M(label,16,DIM)
    return VGroup(VGroup(ic,head,bd),t).arrange(DOWN,buff=0.12)

def node(label, sub=None, color=INK, r=0.3):
    ring=Circle(radius=r,color=color,stroke_width=2,fill_color=BLACK,fill_opacity=1)
    lab=M(label,16,DIM).next_to(ring,DOWN,buff=0.15)
    g=VGroup(ring,lab)
    if sub: g.add(M(sub,13,FAINT).next_to(lab,DOWN,buff=0.06))
    return g

def toggle(label, on=True):
    track=RoundedRectangle(corner_radius=0.2,width=0.9,height=0.42,stroke_width=0,
                           fill_color=(BLUE if on else "#2a2c33"),fill_opacity=1)
    knob=Circle(radius=0.16,color=INK,fill_opacity=1,stroke_width=0).move_to(track)
    knob.shift(RIGHT*0.22 if on else LEFT*0.22)
    t=S(label,20,INK)
    return VGroup(t,VGroup(track,knob)).arrange(RIGHT,buff=0.4)

def mode_cells(s, size=0.62, on_color=RED, off_color=INK):
    """permission octal as tiles; color the leading set-uid digit differently when present."""
    g=VGroup()
    for i,ch in enumerate(s):
        box=RoundedRectangle(corner_radius=0.08,width=size,height=size,stroke_color=LINE,
                             stroke_width=1.5,fill_color=CARD,fill_opacity=1)
        g.add(VGroup(box,Text(ch,font=MONO,font_size=size*58,color=INK).move_to(box)))
    return g.arrange(RIGHT,buff=0.12)


class Base(MovingCameraScene):
    KEY=None; TITLE=""; NUM=""     # NUM like "01", TITLE like "virtual machine"
    def setup(self):
        self._elapsed=0.0; self._events=[]
        self.add(Rectangle(width=config.frame_width*1.2,height=config.frame_height*1.2,
                           stroke_width=0,fill_color=BLACK,fill_opacity=1).set_z_index(-50))
    def play(self,*a,**k): super().play(*a,**k); self._elapsed+=k.get("run_time",1.0)
    def wait(self,d=1.0,**k): super().wait(d,**k); self._elapsed+=d
    def sfx(self,name): self._events.append((round(self._elapsed,3),name))

    def head(self):
        """top-center numbered kicker + bold title (ED header)."""
        k=M(f"{self.NUM} · {self.TITLE}",18,DIM) if self.NUM else M(self.TITLE,18,DIM)
        return k.to_edge(UP,buff=0.6)
    def big_title(self, text):
        return S(text,40,INK,w=BOLD).to_edge(UP,buff=0.95)

    def show_status(self, text, color=INK, old=None, rt=0.4, sound="tick"):
        p=status(text,color).to_edge(DOWN,buff=1.35)   # sits above the caption zone
        if sound: self.sfx(sound)
        if old is not None:
            self.play(FadeOut(old,shift=DOWN*0.15),FadeIn(p,shift=UP*0.15),run_time=rt)
        else:
            self.play(FadeIn(p,shift=UP*0.15),run_time=rt)
        return p

    def glow(self,obj,color=BLUE,rt=0.7,factor=1.35):
        ring=RoundedRectangle(corner_radius=0.18,width=obj.width+0.25,height=obj.height+0.25,
                              stroke_color=color,stroke_width=3,fill_opacity=0).move_to(obj)
        self.add(ring); self.play(ring.animate.scale(factor).set_stroke(width=0,opacity=0),
                                  rate_func=rush_from,run_time=rt); self.remove(ring)

    def finish(self):
        if self.KEY in _DUR:
            rem=_DUR[self.KEY]-self._elapsed
            if rem>0.1: self.wait(rem)
        os.makedirs("out",exist_ok=True)
        if self.KEY: json.dump(self._events,open(f"out/events_{self.KEY}.json","w"))
