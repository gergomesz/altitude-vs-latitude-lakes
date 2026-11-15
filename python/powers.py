import numpy as np
exec(open("improve.py").read().split("feats = {")[0])
SST=np.sum((y-y.mean())**2); side=(lat>33).astype(int); dist=d.coast_km.values
def cv(X, split):
    err=np.zeros(len(y)); groups=side if split else np.zeros(len(y),int)
    for k in range(5):
        for s in np.unique(groups):
            tr=(groups==s)&(fold!=k); te=(groups==s)&(fold==k)
            b=np.linalg.lstsq(np.c_[np.ones(tr.sum()),X[tr]],y[tr],rcond=None)[0]; err[te]=y[te]-np.c_[np.ones(te.sum()),X[te]]@b
    return round(1-np.sum(err**2)/SST,3), round(np.median(abs(err)),2)
# power on elevation
for p in [0.5,1,1.5,2]:
    print("one eq: lat,lat^2, km^%.1f, C, K"%p, cv(np.c_[lat,lat**2,np.clip(km,0,None)**p,lc,R],False))
# let coast effect grow with latitude (lat*C)
print("one eq: lat,lat^2,km,C,lat*C,K", cv(np.c_[lat,lat**2,km,lc,lat*lc,R],False))
print("one eq: lat,lat^2,km,lat*km,C,lat*C,K", cv(np.c_[lat,lat**2,km,lat*km,lc,lat*lc,R],False))
print("split: lat,km,C,lat*C,K", cv(np.c_[lat,km,lc,lat*lc,R],True))
# split + interactions + powers
print("split: lat,km,km^2,C,K", cv(np.c_[lat,km,km**2,lc,R],True))
print("split: lat,km,C,C^2,K", cv(np.c_[lat,km,lc,lc**2,R],True))
print("split: lat,km,C,lat*C,km*C,K", cv(np.c_[lat,km,lc,lat*lc,km*lc,R],True))
