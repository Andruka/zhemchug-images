# Builds the dark-rubric backgrounds: python3 tools/mkdark.py bg/story_soft_nacre_v1.jpg bg/story_dark_v1.jpg 3.5
import sys,numpy as np
from PIL import Image
from scipy import ndimage
STOPS=[(0,(12,31,61)),(.55,(24,55,97)),(.85,(52,88,136)),(1,(96,132,180))]
def gmap(t):
    out=np.zeros(t.shape+(3,),np.float32)
    for (a,ca),(b,cb) in zip(STOPS,STOPS[1:]):
        m=(t>=a)&(t<=b); u=((t-a)/(b-a))[m]
        for j in range(3): out[...,j][m]=ca[j]+(cb[j]-ca[j])*u
    return out
def make(src,dst,sigma,seed=1):
    im=np.asarray(Image.open(src).convert('RGB'),np.float32)
    L=im@np.array([.2126,.7152,.0722],np.float32)
    L=ndimage.gaussian_filter(L,sigma)              # removes JPEG blocks; silk is soft anyway
    lo,hi=np.percentile(L,1),np.percentile(L,97)
    t=np.clip((L-lo)/max(1,hi-lo),0,1)**1.3
    h,w=t.shape; y=np.linspace(0,1,h)[:,None]
    # calmer top (logo) and bottom (contacts): pull toward the dark end there
    shade=1-.28*np.clip(1-y/.22,0,1)-.22*np.clip((y-.72)/.28,0,1)
    t=t*shade
    rgb=gmap(t)
    rng=np.random.default_rng(seed); rgb+=rng.normal(0,1.1,(h,w,1)).astype(np.float32)  # fine grain against banding
    Image.fromarray(np.clip(rgb+.5,0,255).astype(np.uint8)).save(dst,quality=90,subsampling=0,optimize=True)
make(sys.argv[1],sys.argv[2],float(sys.argv[3]))
