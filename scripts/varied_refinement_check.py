"""Compare the varied profiles and verify stable feedback IDs across options."""
from pathlib import Path
import json
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/varied-refinement'
before=json.loads((OUT/'before-options.json').read_text())
after=json.loads((ROOT/'design/nine-dog-review/options.json').read_text())
variants=[o for o in after if o['layout']=='varied']
reference=[p for p in variants[0]['pieces'] if p['category']=='dog']
for o in variants:
    dogs=[p for p in o['pieces'] if p['category']=='dog']
    assert [p['profile_id'] for p in dogs]==list(range(1,10))
    assert all(p['points']==q['points'] for p,q in zip(dogs,reference) if not (o['companion_selection']=='bowl_d' and p['profile_id'] in (1,4)))
    assert all(Polygon(p['points']).contains(__import__('shapely').geometry.Point(p['label_point'])) for p in dogs)
fig,axes=plt.subplots(1,2,figsize=(13,6.5),facecolor='#faf7f0')
for ax,records,title in zip(axes,[before,after],['Before','Refined · stable IDs 1–9']):
    o=next(o for o in records if o['id']=='bones')
    ax.set_facecolor('#e4dfd6')
    for p in o['pieces']:
        if p['category']=='remainder':continue
        poly=Polygon(p['points']);x,y=poly.exterior.xy
        ax.fill(x,y,color='#e1b780' if p['category']=='dog' else '#88b2a1',ec='#695941',lw=.6)
        if 'profile_id' in p and p['profile_id']:
            x,y=p['label_point'];ax.text(x,y,str(p['profile_id']),ha='center',va='center',fontsize=13,color='#294a3c')
    ax.set(xlim=(0,120),ylim=(100,0),aspect='equal',title=f"{title}\n{o['dog_area_percent']}% dogs · {o['remainder_percent']}% remainder with bones")
    ax.set_xlabel('mm');ax.set_ylabel('mm')
fig.tight_layout();fig.savefig(OUT/'comparison.png',dpi=170)
print('Validated nine unique IDs, inside labels, and unchanged dogs except intentional dog-1 and dog-4 shared bowl boundaries.')
