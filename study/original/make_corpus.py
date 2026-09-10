"""Assemble finished literal author parts and prepare masked audits before scoring."""
from pathlib import Path
import collections
import datetime
import itertools
import json
import re
import numpy as np
from experiment import BASE,DATA,MODEL,REVISION,sha

def make():
    assert not (DATA/'frozen_manifest.json').exists()
    assert not (BASE/'results').exists()
    assert not any((DATA/f'audit_labels_{i}.json').exists() for i in [1,2])
    allrows=[];part_hashes={}
    for author in range(4):
        group=[]
        for part in range(5):
            path=DATA/f'authored_{author}_part_{part}.json'
            rows=json.loads(path.read_text())
            assigned=json.loads((DATA/f'assignments_{author}_part_{part}.json').read_text())
            expected={r['id']:r for r in assigned}
            assert len(rows)==len(expected)==12 and len({r['id'] for r in rows})==12
            for r in rows:
                assert all(r.get(k)==v for k,v in expected[r['id']].items())
                for role in ['A','B','C']:
                    text=r[role]
                    assert 40<=len(text.split())<=70,(author,part,r['id'],role,len(text.split()))
                    assert text.endswith('?') and not re.search('[А-Яа-яЁё]',text)
                    assert not re.search(r'\bscenario\s+\d',text,re.I)
            group+=rows;part_hashes[path.name]=sha(path)
        assert len(group)==60
        (DATA/f'authored_{author}.json').write_text(json.dumps(group,indent=2,ensure_ascii=False)+'\n')
        allrows+=group
    allrows=sorted(allrows,key=lambda r:r['id'])
    ids=[r['id']+'_'+role for r in allrows for role in ['A','B','C']]
    texts=[r[role] for r in allrows for role in ['A','B','C']]
    assert len(allrows)==240 and len(texts)==len(set(texts))==720
    assert len({re.sub(r'\s+',' ',t.lower()).strip() for t in texts})==720
    # Inverted index finds repeated word 5-grams without embedding or score access.
    gramsets=[];index=collections.defaultdict(list)
    for i,t in enumerate(texts):
        words=re.findall(r"[a-z]+(?:'[a-z]+)?",t.lower())
        grams={tuple(words[j:j+5]) for j in range(len(words)-4)};gramsets.append(grams)
        for gram in grams:index[gram].append(i)
    pairs=collections.Counter()
    for seen in index.values():
        for pair in itertools.combinations(seen,2):pairs[pair]+=1
    similar=[]
    for (i,j),intersection in pairs.items():
        value=intersection/(len(gramsets[i])+len(gramsets[j])-intersection)
        if value>.5:similar.append({'id_1':ids[i],'id_2':ids[j],'fivegram_jaccard':value})
    from transformers import AutoTokenizer
    path=BASE.parents[1]/'.hf_cache'/('models--'+MODEL.replace('/','--'))/'snapshots'/REVISION
    tokenizer=AutoTokenizer.from_pretrained(str(path),local_files_only=True)
    lengths=[len(t) for t in tokenizer(texts,truncation=False)['input_ids']]
    assert max(lengths)<=128,('No truncation allowed',max(lengths))
    source=BASE.parents[1]/'notebooks/concept_layers_triplets/data/anchors_multi.npz'
    assert np.array_equal(np.load(source)['anchors'],np.load(DATA/'anchors_multi.npz')['anchors'])
    provenance={'source_anchor_path':str(source.relative_to(BASE.parents[1])),'source_anchor_sha256':sha(source),
      'copied_array_exact':True,'model_id':MODEL,'revision':REVISION,
      'python_model_weights_sha256':sha(path/'model.safetensors'),
      'app_model_config':'DecisionKernel/Resources/Models/paraphrase-multilingual-MiniLM-L12-v2/config.json',
      'app_config_matches_python':sha(BASE.parents[1]/'DecisionKernel/Resources/Models/paraphrase-multilingual-MiniLM-L12-v2/config.json')==sha(path/'config.json'),
      'author_part_sha256':part_hashes,'authorship':'Four AI author sequences with five literal parts each, gpt-5.6-sol, after rejected template attempt.'}
    (DATA/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    (DATA/'triplets.json').write_text(json.dumps(allrows,indent=2,ensure_ascii=False)+'\n')
    audit={'assembled_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'n_triplets':240,'n_unique_texts':720,
      'word_count_min':min(len(t.split()) for t in texts),'word_count_max':max(len(t.split()) for t in texts),
      'token_lengths':dict(zip(ids,lengths)),'max_tokens':max(lengths),'no_truncation':True,
      'fivegram_jaccard_above_half':similar,'before_new_embeddings':True}
    (DATA/'pre_score_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    for auditor,seed in [(1,20262912),(2,20262913)]:
        rng=np.random.default_rng(seed)
        sides=np.array(['X']*120+['Y']*120);rng.shuffle(sides)
        masked=[];key={}
        for r,side in zip(allrows,sides):
            key[r['id']]=str(side)
            masked.append({'id':r['id'],'A':r['A'],'X':r['B'] if side=='X' else r['C'],'Y':r['C'] if side=='X' else r['B']})
        rng.shuffle(masked)
        (DATA/f'audit_input_{auditor}.json').write_text(json.dumps(masked,indent=2,ensure_ascii=False)+'\n')
        (DATA/f'audit_key_{auditor}.json').write_text(json.dumps(key,indent=2)+'\n')
        for part in range(6):
            (DATA/f'audit_input_{auditor}_part_{part}.json').write_text(json.dumps(masked[40*part:40*(part+1)],indent=2,ensure_ascii=False)+'\n')
    print('Assembled 240 triplets / 720 texts; words',audit['word_count_min'],audit['word_count_max'],'max tokens',max(lengths),'near duplicates',len(similar))
if __name__=='__main__':make()
