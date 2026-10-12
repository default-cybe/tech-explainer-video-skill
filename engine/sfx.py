#!/usr/bin/env python
"""Procedural SFX + ambient music bed, placed from per-scene event logs. No downloads.
Usage: sfx.py <total_seconds> <key1> <key2> ...   (keys in play order; reads out/events_<key>.json
and audio/<key>.wav for per-scene durations). Writes out/sfx.wav and out/music.wav at <total_seconds>."""
import sys, json, os, numpy as np, soundfile as sf

SR=48000

def env(n, a=0.005, d=0.1, kind="exp"):
    t=np.arange(n)/SR
    at=np.clip(t/max(a,1e-4),0,1)
    if kind=="exp": de=np.exp(-t/max(d,1e-4))
    else: de=np.clip(1-(t-a)/max(d,1e-4),0,1)
    return at*de

def tone(f, n, f_end=None):
    t=np.arange(n)/SR
    if f_end: f=np.linspace(f,f_end,n)
    return np.sin(2*np.pi*(np.cumsum(f)/SR if np.ndim(f) else f*t))

def pop(vol=0.5):
    n=int(0.08*SR); s=tone(np.linspace(900,320,n),n)*env(n,0.002,0.07); return s*vol
def click(vol=0.4):
    n=int(0.018*SR); s=(np.random.randn(n))*env(n,0.001,0.012); return s*vol
def tick(vol=0.35):
    n=int(0.03*SR); s=tone(1600,n)*env(n,0.001,0.02); return s*vol
def whoosh(vol=0.4):
    n=int(0.33*SR); noise=np.random.randn(n)
    # simple one-pole bandpass sweep via moving diff + envelope
    f=np.linspace(0.02,0.25,n); y=np.zeros(n); prev=0.0
    for i in range(n):  # cheap resonator sweep
        prev=prev+f[i]*(noise[i]-prev); y[i]=noise[i]-prev
    e=np.sin(np.pi*np.arange(n)/n)**1.5
    return y*e*vol
def ding(vol=0.45):
    n=int(0.6*SR); s=(tone(880,n)+0.6*tone(1320,n)+0.3*tone(1760,n))*env(n,0.002,0.4)
    return s*vol/1.9
def impact(vol=0.7):
    n=int(0.4*SR); s=(tone(np.linspace(140,55,n),n)*1.0 + 0.5*np.random.randn(n))*env(n,0.002,0.33)
    return s*vol
def rise(vol=0.4):
    n=int(0.5*SR); s=tone(np.linspace(220,660,n),n)*env(n,0.01,0.45,"lin"); return s*vol

GEN=dict(pop=pop,click=click,tick=tick,whoosh=whoosh,ding=ding,impact=impact,rise=rise,boom=impact)

def place(bed, clip, t0):
    i=int(t0*SR); j=min(len(bed),i+len(clip))
    if i<len(bed): bed[i:j]+=clip[:j-i]

def music(total):
    """Soft ambient pad: slow root/fifth/octave with tremolo. Low level."""
    n=int(total*SR); t=np.arange(n)/SR
    base=55.0  # A1
    chords=[(1,1.5,2.0),(1.2,1.8,2.4)]  # two moods
    out=np.zeros(n)
    seg=12.0
    for k in range(int(total//seg)+1):
        c=chords[k%len(chords)]; i0=int(k*seg*SR); i1=min(n,int((k+1)*seg*SR))
        if i0>=n: break
        tt=t[i0:i1]
        pad=sum(np.sin(2*np.pi*base*r*tt) + 0.5*np.sin(2*np.pi*base*2*r*tt) for r in c)
        a=np.clip((tt-k*seg)/2,0,1)*np.clip(((k+1)*seg-tt)/2,0,1)  # fade seg edges
        out[i0:i1]+=pad*a
    out*=0.5/ (np.max(np.abs(out))+1e-6)
    out*=0.10  # quiet bed
    trem=0.85+0.15*np.sin(2*np.pi*0.08*t)
    return out*trem

def main():
    total=float(sys.argv[1]); keys=sys.argv[2:]
    n=int(total*SR); sfx=np.zeros(n)
    offset=0.0
    for key in keys:
        dur=sf.info(f"audio/{key}.wav").frames/sf.info(f"audio/{key}.wav").samplerate
        ev=[]
        p=f"out/events_{key}.json"
        if os.path.exists(p): ev=json.load(open(p))
        for t0,name in ev:
            g=GEN.get(name)
            if g: place(sfx, g(), offset+t0)
        offset+=dur
    sfx*=0.9/(np.max(np.abs(sfx))+1e-6)*0.9
    sf.write("out/sfx.wav", sfx, SR)
    sf.write("out/music.wav", music(total), SR)
    print(f"sfx+music written @ {total:.1f}s, {sum(1 for k in keys for _ in (json.load(open(f'out/events_{k}.json')) if os.path.exists(f'out/events_{k}.json') else []))} cues")

if __name__=="__main__": main()
