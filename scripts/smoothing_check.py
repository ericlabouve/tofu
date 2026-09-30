"""Validate the review partition and render a local before/after back-contour check."""
from pathlib import Path
import json
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/smoothing-review'
before=json.loads((OUT/'before-options.json').read_text())
after=json.loads((ROOT/'design/nine-dog-review/options.json').read_text())
sheet=box(0,0,120,100)
for o in after:
    ps=[Polygon(p['points'],p['holes']) for p in o['pieces']]
    assert all(p.is_valid for p in ps),o['id']
    union=unary_union(ps)
    assert sheet.symmetric_difference(union).area<.01,o['id']
    assert abs(sum(p.area for p in ps)-union.area)<.01,o['id']
    assert len([p for p in o['pieces'] if p['category']=='dog'])==o['dogs']
old=np.array(next(o for o in before if o['id']=='a6')['pieces'][0]['points'])
new=np.array(next(o for o in after if o['id']=='a6')['pieces'][0]['points'])
fig,ax=plt.subplots(1,2,figsize=(12,6),gridspec_kw={'width_ratios':[1,1.3]},facecolor='#fffdf8')
for a in ax:
    a.fill(new[:,0],new[:,1],color='#e3ba85',alpha=.6)
    a.plot(old[:,0],old[:,1],color='#ab685a',linestyle='--',lw=1.4,label='Before')
    a.plot(new[:,0],new[:,1],color='#365d4a',lw=1.6,label='After')
    a.set_aspect('equal');a.spines[['top','right']].set_visible(False);a.set_xlabel('mm')
ax[0].set_xlim(0,53);ax[0].set_ylim(65,-3);ax[0].set_title('Same A profile · shared curves refined',fontsize=12)
ax[1].set_xlim(31.5,42);ax[1].set_ylim(23.1,19.8);ax[1].set_title('Back / neighboring paw connection',fontsize=12);ax[1].legend(loc='lower right')
fig.suptitle('REMOVING THE SMALL BACK HUMP',x=.07,ha='left',fontsize=20)
fig.text(.07,.05,'Contour smoothing changes the silhouette. The blade cutting edge remains a separate sharp-edge requirement.',fontsize=11,color='#756956')
fig.subplots_adjust(top=.84,bottom=.16,wspace=.3)
fig.savefig(OUT/'smoothing-comparison.png',dpi=170)
# Quantify the local crest against an endpoint baseline, on the same drawing interval.
def prominence(points):
    part=points[(points[:,0]>=33)&(points[:,0]<=40.5)&(points[:,1]>=20)&(points[:,1]<=22.5)]
    part=part[np.argsort(part[:,0])]
    x,idx=np.unique(part[:,0],return_index=True);y=part[idx,1]
    trend=np.interp(x,[x[0],x[-1]],[y[0],y[-1]])
    return float(np.max(trend-y))
metrics=dict(valid_layout_partitions=len(after),back_crest_before_mm=prominence(old),back_crest_after_mm=prominence(new),comparison_interval_mm=[33,40.5])
(OUT/'checks.json').write_text(json.dumps(metrics,indent=2))
print(metrics)
