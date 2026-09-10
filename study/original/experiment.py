"""Frozen English-only conflict-over-topic evaluation, 240 unique triplets."""
from pathlib import Path
import hashlib
import json
import importlib.metadata
import platform
import numpy as np
import pandas as pd

BASE=Path(__file__).resolve().parent
DATA,RESULTS=BASE/'data',BASE/'results'
MODEL='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
REVISION='e8f8c211226b894fcb81acc59f3b34ba3efd5f42'
SEED=20260911
METHODS=['embedding','concept207','hybrid50']
CONTRASTS=[('hybrid50','embedding'),('concept207','embedding'),('hybrid50','concept207')]
FROZEN=['PROTOCOL.md','PRE_SCORE_AMENDMENT.md','experiment.py','check_metrics.py','requirements.txt','make_corpus.py',
 'PRE_SCORE_AUDIT_REPAIR.md','data/audit_initial/audit_labels_1.json','data/audit_initial/audit_labels_2.json',
 'data/triplets.json','data/anchors_multi.npz','data/provenance.json','data/pre_score_audit.json',
 'data/design_manifest.json','data/assignments.json','data/label_definitions.json','data/domains.json',
 'data/audit_input_1.json','data/audit_input_2.json','data/audit_key_1.json','data/audit_key_2.json',
 'data/audit_labels_1.json','data/audit_labels_2.json','data/notebook_code_manifest.json']+[f'data/assignments_{i}.json' for i in range(4)]+[f'data/authored_{i}.json' for i in range(4)]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def norm(x):
    x=np.asarray(x,dtype=float);length=np.linalg.norm(x,axis=-1,keepdims=True)
    assert np.all(length>1e-12)
    return x/length
def verify_freeze():
    m=json.loads((DATA/'frozen_manifest.json').read_text())
    assert set(m['sha256'])==set(FROZEN)
    for p,h in m['sha256'].items():assert sha(BASE/p)==h,p
    design=json.loads((DATA/'design_manifest.json').read_text())
    for p,h in design['sha256'].items():assert sha(BASE/p)==h,p
    return m
def read_data():
    rows=pd.DataFrame(json.loads((DATA/'triplets.json').read_text())).sort_values('id').reset_index(drop=True)
    assert len(rows)==rows.id.nunique()==240
    assert rows.groupby(['conflict','anchor_topic']).size().eq(2).all()
    assert rows.groupby(['author','conflict']).size().eq(5).all()
    assert rows.groupby(['author','anchor_topic']).size().eq(6).all()
    texts=[r[k] for r in rows.to_dict('records') for k in ['A','B','C']]
    assert len(texts)==len(set(texts))==720
    for i in [1,2]:
        audit=pd.DataFrame(json.loads((DATA/f'audit_labels_{i}.json').read_text())).set_index('id')
        key=json.loads((DATA/f'audit_key_{i}.json').read_text())
        assert len(audit)==audit.index.nunique()==240 and set(audit.index)==set(rows.id)
        assert set(audit.choice).issubset({'X','Y','both','neither'})
        assert set(audit.confidence).issubset({'high','medium','low'})
        assert audit.explanation.map(lambda x:isinstance(x,str) and len(x)>0).all()
        normalized={rid: ('B' if choice==key[rid] else 'C') if choice in ['X','Y'] else choice for rid,choice in audit.choice.items()}
        rows[f'audit_{i}']=rows.id.map(normalized)
        rows[f'audit_{i}_agrees']=rows[f'audit_{i}'].eq('B')
    rows['both_audits_agree']=rows.audit_1_agrees & rows.audit_2_agrees
    return rows,texts
def encode(texts):
    import torch
    from sentence_transformers import SentenceTransformer
    torch.set_num_threads(4);torch.manual_seed(SEED)
    local=BASE.parents[1]/'.hf_cache'/('models--'+MODEL.replace('/','--'))/'snapshots'/REVISION
    model=(SentenceTransformer(str(local),device='cpu',local_files_only=True) if (local/'modules.json').exists()
           else SentenceTransformer(MODEL,revision=REVISION,device='cpu'))
    model.max_seq_length=128
    lengths=[len(t) for t in model.tokenizer(texts,truncation=False)['input_ids']]
    assert max(lengths)<=128,('No silent truncation',max(lengths))
    spec={'texts':texts,'model':MODEL,'revision':REVISION,'device':'cpu',
          'packages':{p:importlib.metadata.version(p) for p in ['torch','transformers','sentence-transformers']}}
    cache=BASE/'.cache';cache.mkdir(exist_ok=True)
    path=cache/(hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest()+'.npy')
    if path.exists():z=np.load(path,allow_pickle=False)
    else:
        z=norm(model.encode(texts,batch_size=32,normalize_embeddings=False,show_progress_bar=False,convert_to_numpy=True))
        np.save(path,z,allow_pickle=False)
    assert z.shape==(720,384)
    return z,lengths
def evaluate(vectors,ids=None):
    v=norm(vectors).reshape(-1,3,np.asarray(vectors).shape[-1])
    ab=1-np.einsum('ij,ij->i',v[:,0],v[:,1]);ac=1-np.einsum('ij,ij->i',v[:,0],v[:,2])
    margin=ac-ab
    return pd.DataFrame({'id':list(ids) if ids is not None else np.arange(len(v)),
      'd_same_conflict':ab,'d_same_topic':ac,'margin':margin,'score':(margin>0).astype(float)+.5*(margin==0)})
def mixture(z,c):
    h=np.concatenate([np.sqrt(.5)*z,np.sqrt(.5)*c],axis=1)
    assert np.allclose(np.linalg.norm(h,axis=1),1,atol=1e-12)
    return h
def paired_intervals(main):
    labels=list(json.loads((DATA/'label_definitions.json').read_text()))
    topics=json.loads((DATA/'domains.json').read_text())
    out=[];loo=[]
    for method,baseline in CONTRASTS:
        a=main[main.method.eq(method)].set_index('id')
        b=main[main.method.eq(baseline)].set_index('id').loc[a.index]
        difference=a[['score','margin']]-b[['score','margin']]
        difference['conflict']=a.conflict;difference['anchor_topic']=a.anchor_topic;difference['variant']=a.variant
        grid=(difference.set_index(['conflict','anchor_topic','variant'])[['score','margin']]
              .reindex(pd.MultiIndex.from_product([labels,topics,[0,1]])))
        assert not grid.isna().any().any()
        grid=grid.to_numpy().reshape(12,10,2,2).mean(axis=2)
        for grouping in ['conflict_and_topic','conflict','anchor_topic']:
            rng=np.random.default_rng(SEED)
            if grouping=='conflict_and_topic':
                ki=rng.integers(0,12,size=(10000,12));ti=rng.integers(0,10,size=(10000,10))
                samples=grid[ki[:,:,None],ti[:,None,:]].mean(axis=(1,2))
            else:
                blocks=grid.mean(axis=1 if grouping=='conflict' else 0)
                draws=rng.integers(0,len(blocks),size=(10000,len(blocks)))
                samples=blocks[draws].mean(axis=1)
            for j,metric in enumerate(['accuracy','mean_margin']):
                low,high=np.quantile(samples[:,j],[.025,.975])
                out.append(dict(method=method,baseline=baseline,grouping=grouping,metric=metric,
                   difference=float(grid[:,:,j].mean()),low=float(low),high=float(high)))
        for author in range(4):
            keep=a.author.ne(author)
            loo.append(dict(method=method,baseline=baseline,excluded_author=author,n_triplets=int(keep.sum()),
                       accuracy_difference=float(difference.loc[keep,'score'].mean()),margin_difference=float(difference.loc[keep,'margin'].mean())))
    return pd.DataFrame(out),pd.DataFrame(loo)

def run():
    verify_freeze();rows,texts=read_data();RESULTS.mkdir(exist_ok=True)
    print('Encoding 720 English paragraphs with the fixed Dilemma model.',flush=True)
    z,lengths=encode(texts)
    anchors=np.load(DATA/'anchors_multi.npz',allow_pickle=False)['anchors']
    assert anchors.shape==(207,384) and np.allclose(np.linalg.norm(anchors,axis=1),1)
    centered=anchors-anchors.mean(axis=0);c=norm(z@centered.T);h=mixture(z,c)
    reps={'embedding':z,'concept207':c,'hybrid50':h}
    meta=rows.drop(columns=['A','B','C'])
    main=pd.concat([evaluate(v,rows.id).assign(method=m).merge(meta,on='id',validate='one_to_one') for m,v in reps.items()],ignore_index=True)
    wide=main.pivot(index='id',columns='method',values='margin')
    assert np.allclose(wide.hybrid50,.5*(wide.embedding+wide.concept207),atol=1e-12)
    summary=main.groupby('method',as_index=False).agg(n_triplets=('score','size'),correct_score=('score','sum'),accuracy=('score','mean'),mean_margin=('margin','mean'))
    intervals,loo=paired_intervals(main)
    np.savez_compressed(RESULTS/'main_vectors.npz',ids=np.array([r['id']+'_'+k for r in rows.to_dict('records') for k in ['A','B','C']]),**reps)
    accepted=rows[rows.both_audits_agree]
    sensitivity=main[main.both_audits_agree].groupby('method',as_index=False).agg(n_triplets=('score','size'),correct_score=('score','sum'),accuracy=('score','mean'),mean_margin=('margin','mean'))
    sensitivity['n_conflicts']=accepted.conflict.nunique();sensitivity['n_topics']=accepted.anchor_topic.nunique()
    sensitivity['interpretable']=len(accepted)>=120 and accepted.conflict.nunique()>=8 and accepted.anchor_topic.nunique()>=6
    initial_masks=[]
    for auditor in [1,2]:
        initial=json.loads((DATA/f'audit_initial/audit_labels_{auditor}.json').read_text())
        key=json.loads((DATA/f'audit_key_{auditor}.json').read_text())
        agrees={r['id']:r['choice']==key[r['id']] for r in initial}
        assert len(agrees)==240 and set(agrees)==set(rows.id)
        initial_masks.append(rows.id.map(agrees))
    initial_accepted=rows[initial_masks[0]&initial_masks[1]]
    initial_sensitivity=main[main.id.isin(initial_accepted.id)].groupby('method',as_index=False).agg(
        n_triplets=('score','size'),correct_score=('score','sum'),accuracy=('score','mean'),mean_margin=('margin','mean'))
    initial_sensitivity['n_conflicts']=initial_accepted.conflict.nunique();initial_sensitivity['n_topics']=initial_accepted.anchor_topic.nunique()
    initial_sensitivity['interpretable']=len(initial_accepted)>=120 and initial_accepted.conflict.nunique()>=8 and initial_accepted.anchor_topic.nunique()>=6
    transitions=[]
    scores=main.pivot(index='id',columns='method',values='score')
    for method,baseline in CONTRASTS:
        transitions.append({'method':method,'baseline':baseline,'improved_triplets':int(scores[method].gt(scores[baseline]).sum()),
           'worsened_triplets':int(scores[method].lt(scores[baseline]).sum()),'unchanged_triplets':int(scores[method].eq(scores[baseline]).sum())})
    singular=np.linalg.svd(centered,compute_uv=False)
    control_records=[];map_specs=[];map_checks=[]
    for family in ['gaussian','spectrum_matched']:
        for replicate in range(30):
            map_seed=SEED+replicate+(1000 if family=='spectrum_matched' else 0)
            g=np.random.default_rng(map_seed).standard_normal((384,207))
            if family=='gaussian':matrix=g/np.sqrt(207)
            else:
                q,r=np.linalg.qr(g,mode='reduced');q=q*np.where(np.diag(r)<0,-1.,1.)
                matrix=q*singular
                err=float(np.max(np.abs(matrix.T@matrix-np.diag(singular**2))))
                assert err<1e-10
                map_checks.append({'replicate':replicate,'map_seed':map_seed,'gram_spectrum_error':err})
            random_c=norm(z@matrix)
            map_specs.append({'family':family,'replicate':replicate,'map_seed':map_seed,'input_dimension':384,'output_dimension':207})
            for blend,v in [('projection',random_c),('hybrid50',mixture(z,random_c))]:
                control_records.append(evaluate(v,rows.id).assign(family=family,replicate=replicate,map_seed=map_seed,blend=blend))
    controls=pd.concat(control_records,ignore_index=True)
    cs=controls.groupby(['family','replicate','map_seed','blend'],as_index=False).agg(correct_score=('score','sum'),accuracy=('score','mean'),mean_margin=('margin','mean'))
    distributions=[]
    for (family,blend),group in cs.groupby(['family','blend']):
        reference=summary.set_index('method').loc['concept207' if blend=='projection' else 'hybrid50']
        distributions.append({'family':family,'blend':blend,'n_maps':len(group),
         'accuracy_min':group.accuracy.min(),'accuracy_median':group.accuracy.median(),'accuracy_p95':group.accuracy.quantile(.95),'accuracy_max':group.accuracy.max(),
         'n_accuracy_strictly_above_concept':int(group.accuracy.gt(reference.accuracy).sum()),'n_accuracy_equal_concept':int(group.accuracy.eq(reference.accuracy).sum()),
         'margin_min':group.mean_margin.min(),'margin_median':group.mean_margin.median(),'margin_max':group.mean_margin.max()})
    (RESULTS/'random_map_specs.json').write_text(json.dumps(map_specs,indent=2)+'\n')
    tables={'per_triplet':main,'summary':summary,'intervals':intervals,'leave_one_author_out':loo,'agreed_audit_sensitivity':sensitivity,'initial_audit_sensitivity':initial_sensitivity,
     'transitions':pd.DataFrame(transitions),'random_per_triplet':controls,'random_summary':cs,'random_distributions':pd.DataFrame(distributions),
     'audit_by_conflict':rows.groupby('conflict',as_index=False).agg(n=('id','size'),auditor_1_agrees=('audit_1_agrees','sum'),auditor_2_agrees=('audit_2_agrees','sum'),both_agree=('both_audits_agree','sum'))}
    for factor in ['conflict','anchor_topic','author']:
        tables['by_'+factor]=main.groupby([factor,'method'],as_index=False).agg(
            n_triplets=('score','size'),correct_score=('score','sum'),accuracy=('score','mean'),mean_margin=('margin','mean'))
    for name,t in tables.items():t.to_csv(RESULTS/f'{name}.csv',index=False,float_format='%.12g')
    rows[['id','audit_1','audit_2','audit_1_agrees','audit_2_agrees','both_audits_agree']].to_csv(RESULTS/'audit_agreements.csv',index=False)
    env={'model':MODEL,'revision':REVISION,'embedding_dimension':384,'concept_dimension':207,'hybrid_dimension':591,'device':'cpu','seed':SEED,
     'n_triplets':240,'n_texts':720,'token_lengths':lengths,'max_sequence_length':128,
     'both_audits_agree_count':int(rows.both_audits_agree.sum()),'auditor_1_agrees_count':int(rows.audit_1_agrees.sum()),'auditor_2_agrees_count':int(rows.audit_2_agrees.sum()),
     'initial_audit_agreements':[int(m.sum()) for m in initial_masks],'initial_both_audits_agree_count':int(len(initial_accepted)),
     'auditors_same_normalized_choice_count':int(rows.audit_1.eq(rows.audit_2).sum()),
     'frozen_manifest_sha256':sha(DATA/'frozen_manifest.json'),'python':platform.python_version(),
     'packages':{p:importlib.metadata.version(p) for p in ['numpy','pandas','sentence-transformers','torch','transformers','matplotlib','nbformat','nbclient']},'random_map_checks':map_checks}
    (RESULTS/'environment.json').write_text(json.dumps(env,indent=2,ensure_ascii=False)+'\n')
    print(summary.to_string(index=False),flush=True)
    print(intervals[intervals.metric.eq('accuracy')].to_string(index=False),flush=True)
    return rows,tables,env
if __name__=='__main__':run()
