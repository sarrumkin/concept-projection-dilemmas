"""Known-answer triplets and independent cosine reference, no new scores."""
import numpy as np
import json
import pandas as pd
from scipy.spatial.distance import cosine
from experiment import DATA,norm,evaluate,mixture,paired_intervals

def check():
    good=np.tile(np.array([[1.,0.],[1.,0.],[0.,1.]]),(240,1))
    assert evaluate(good).score.eq(1).all() and evaluate(good).margin.eq(1).all()
    bad=good.reshape(240,3,2)[:,[0,2,1],:].reshape(720,2)
    assert evaluate(bad).score.eq(0).all() and evaluate(bad).margin.eq(-1).all()
    assert evaluate(np.ones((720,4))).score.eq(.5).all()
    rng=np.random.default_rng(7412);z=norm(rng.normal(size=(720,16)));c=norm(rng.normal(size=(720,7)))
    assert np.allclose(evaluate(mixture(z,c)).margin,.5*(evaluate(z).margin+evaluate(c).margin))
    for i in [0,71,239]:
        a,b,d=z[3*i:3*i+3];r=evaluate(z).iloc[i]
        assert np.isclose(r.d_same_conflict,cosine(a,b)) and np.isclose(r.d_same_topic,cosine(a,d))
    assigned=pd.DataFrame(json.loads((DATA/'assignments.json').read_text()))
    known=pd.concat([assigned.assign(method=m,score=value,margin=value) for m,value in [('embedding',0.),('concept207',.5),('hybrid50',1.)]])
    intervals,loo=paired_intervals(known)
    expected={('hybrid50','embedding'):1.,('concept207','embedding'):.5,('hybrid50','concept207'):.5}
    for r in intervals.itertuples():
        assert r.difference==r.low==r.high==expected[(r.method,r.baseline)]
    assert loo.n_triplets.eq(180).all()
    print('Passed: ideal semantic/topic geometry, ties, mixture identity, scipy cosine.')
if __name__=='__main__':check()
