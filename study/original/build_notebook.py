from pathlib import Path
import nbformat as nbf

BASE=Path(__file__).resolve().parent
md,code=nbf.v4.new_markdown_cell,nbf.v4.new_code_cell
nb=nbf.v4.new_notebook()
nb.cells=[
md("""# 09. English conflict-over-topic: 240 новых троек

**Цель:** проверить, помогает ли фиксированный концепт-профиль находить одинаковый конфликт вопреки тематическому отвлечению. 720 новых английских абзацев; 240 уникальных троек A/B/C, без повторного использования текстов. Три прежних примера исключены.

Модель Dilemma — **paraphrase-multilingual-MiniLM-L12-v2, 384D**. Сравниваем embedding, concept207 и hybrid50. Основная разность — hybrid50 − embedding по точности предпочтения d(A,B)<d(A,C). Все другие исходы и случайные контроли также опубликованы.

[Протокол](PROTOCOL.md), [поправка до scoring](PRE_SCORE_AMENDMENT.md), [читаемый отчёт](research_note.md). Набор и аудиты подготовлены с AI-помощью, без человеческого gold standard.
"""),
code("""import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display,Markdown
from experiment import BASE,DATA,RESULTS,METHODS,run,verify_freeze
pd.set_option('display.max_columns',None);pd.set_option('display.max_colwidth',110)
plt.rcParams.update({'figure.dpi':115,'axes.spines.top':False,'axes.spines.right':False})
manifest=verify_freeze()
display(Markdown('Входы фиксированы до первого нового scoring: **'+manifest['frozen_at_utc']+'**.'))
rows,tables,environment=run()
main,summary,intervals=tables['per_triplet'],tables['summary'],tables['intervals']
FIG=RESULTS/'figures';FIG.mkdir(exist_ok=True)
"""),
md("""## Набор и два аудита до scoring

12 конфликтов × 10 тем × 2 варианта. Четыре AI-авторские последовательности по 60 троек. Первые большие шаблонные генерации отклонены **до** аудитов и embeddings; окончательные тексты написаны по 12 троек отдельными буквальными историями. Изменение процедуры раскрыто в поправке, исходный дизайн сохранён.

Аудиторы получили только A, X, Y со случайным порядком кандидатов, без ролей B/C, авторских классов, тем и scores. Они выбирали совпадение основных конкурирующих ставок: X, Y, both или neither. Ни аудиторское согласие, ни общий размер корпуса не устраняют зависимость AI-стиля и размеченных определений.

До scoring обнаружены несоответствия буквы тексту объяснения. Для каждого исходного аудита отдельный AI-проверяющий сверил кодирование всех ответов без раскрытия ключей; первоначальные объяснения и версии сохранены. Процедура, неудачная промежуточная попытка и начальные согласия раскрыты в [отдельном уточнении](PRE_SCORE_AUDIT_REPAIR.md); итоговый отчёт показывает чувствительность и по первым ответам. Это дополнительная проверка, не ещё два независимых смысловых голоса.
"""),
code("""display(pd.crosstab(rows.conflict,rows.anchor_topic))
display(tables['audit_by_conflict'])
display(Markdown(f"Аудитор 1 согласился с автором: **{environment['auditor_1_agrees_count']}/240**; аудитор 2: **{environment['auditor_2_agrees_count']}/240**; оба: **{environment['both_audits_agree_count']}/240**."))
display(pd.crosstab(rows.audit_1,rows.audit_2))
display(rows.loc[~rows.both_audits_agree,['id','conflict','anchor_topic','audit_1','audit_2']].head(30))
display(Markdown('Всего **720 уникальных английских текстов**. Максимальная длина: **'+str(max(environment['token_lengths']))+' токенов**, лимит 128.'))
"""),
md(r"""## Геометрия и основная метрика

$$z=\operatorname{norm}(encoder(text)),\quad c=\operatorname{norm}(z(A-\operatorname{mean}_{rows}A)^T),\quad h=[\sqrt{0.5}z;\sqrt{0.5}c].$$

A — та же карта 207 атрибутов Bhatia. Encoder и карта не обучаются на новых метках. Размерности: z — 384, c — 207, h — 591. Расстояние hybrid равно среднему двух расстояний компонентов.

Положительный $m=d(A,C)-d(A,B)$ означает правильное предпочтение одинакового конфликта, отрицательный — предпочтение темы. Точное равенство даёт 0.5 балла. Основная точность — средний балл по 240 тройкам. Margin описателен и не является калиброванной уверенностью.
"""),
code("""display(summary.round(5))
display(tables['transitions'])
fig,ax=plt.subplots(figsize=(7.5,4))
s=summary.set_index('method').loc[METHODS]
ax.bar(['Embedding 384D','Concept 207','Hybrid 50/50'],s.accuracy,color=['#334155','#d97706','#078d82'])
for i,r in enumerate(s.itertuples()):ax.text(i,r.accuracy+.025,f'{r.correct_score:g}/240 ({r.accuracy:.1%})',ha='center')
ax.set_ylim(0,1.05);ax.set_ylabel('Correct conflict-over-topic preferences')
ax.axhline(.5,color='#9ca3af',linestyle='--',label='Random choice of candidate, not random projection')
ax.legend(fontsize=8,loc='lower right');fig.tight_layout();fig.savefig(FIG/'accuracy.png',dpi=180);plt.show()
"""),
md("""## Разности и устойчивость

Основной 95% интервал: 10 000 парных двухфакторных bootstrap-перевзвешиваний 12 конфликтов и 10 anchor-тем, оба варианта клетки сохраняются. Дополнительно — группировки по одному фактору и исключение каждого из четырёх авторов. Это описательная чувствительность фиксированной синтетической сетки, не population CI.

Рабочий ориентир +5 п.п. и нижняя граница основного интервала выше нуля был зафиксирован как **допущение ассистента**, поскольку вопрос о пороге остался без ответа. Точные числа публикуются независимо от его достижения.
"""),
code("""primary=intervals[(intervals.method=='hybrid50')&(intervals.baseline=='embedding')&(intervals.metric=='accuracy')]
display(primary.round(5))
display(intervals[intervals.metric.eq('accuracy')].round(5))
display(tables['leave_one_author_out'].round(5))
by_conflict=main.groupby(['conflict','method']).score.mean().unstack()
by_conflict['hybrid_minus_embedding']=by_conflict.hybrid50-by_conflict.embedding
display(by_conflict.round(4))
fig,ax=plt.subplots(figsize=(10,5))
delta=by_conflict.hybrid_minus_embedding.sort_values()
ax.barh(delta.index,delta.values,color=['#b45309' if v<0 else '#078d82' for v in delta])
ax.axvline(0,color='#64748b');ax.set_xlabel('Hybrid minus embedding accuracy; 20 triplets per conflict')
fig.tight_layout();fig.savefig(FIG/'conflict_differences.png',dpi=180);plt.show()
display(tables['agreed_audit_sensitivity'].round(5))
"""),
md("""## Случайные карты

30 Gaussian-проекций в 207 координат и 30 случайных ориентаций с тем же спектром, что у концепт-карты. Для каждой — отдельный профиль и его смесь 50/50 с z. Все seeds назначены до scores. Карты используют тот же семантический embedding, поэтому их точность не обязана равняться 50%.

Доли превышений и 95-й percentile здесь описывают выбранные карты на **тех же** 240 тройках: это не p-values и не 60 независимых датасетов. Прирост относительно embedding и преимущество над случайными картами — разные утверждения.
"""),
code("""display(tables['random_distributions'].round(5))
controls=tables['random_summary']
fig,axes=plt.subplots(1,2,figsize=(11,4),sharey=True)
for ax,blend,target in zip(axes,['projection','hybrid50'],['concept207','hybrid50']):
    sub=controls[controls.blend.eq(blend)]
    bins=np.linspace(sub.accuracy.min()-.01,sub.accuracy.max()+.01,13)
    for family,color in [('gaussian','#64748b'),('spectrum_matched','#9d78ba')]:
        ax.hist(sub[sub.family.eq(family)].accuracy,bins=bins,alpha=.55,label=family,color=color)
    ax.axvline(float(summary[summary.method.eq(target)].accuracy.iloc[0]),color='#d97706',linewidth=2,label=target)
    ax.set_title(blend);ax.set_xlabel('Accuracy on the same 240 triplets');ax.legend(fontsize=8)
axes[0].set_ylabel('Number of random maps');fig.tight_layout();fig.savefig(FIG/'random_controls.png',dpi=180);plt.show()
"""),
md("""## Примеры без отбора по результату

Три минимальных случайных ID из зафиксированного корпуса. Это иллюстрация, а не отдельное доказательство. Все остальные абзацы сохранены в `data/triplets.json`; все спорные оценки аудиторов доступны в исходных JSON.
"""),
code("""for r in rows.head(3).to_dict('records'):
    display(Markdown('### '+r['id']+' — '+r['conflict']))
    for role in ['A','B','C']:display(Markdown('**'+role+'** — '+r[role]))
    display(main[main.id.eq(r['id'])][['method','d_same_conflict','d_same_topic','margin','score']].round(5))
verify_freeze()
assert len(main)==720 and len(tables['random_per_triplet'])==28800
display(Markdown('Все 240 троек × 3 основных метода и 28 800 контрольных оценок сохранены. Итог и ограничения: [research_note.md](research_note.md).'))
""")]
nb.metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'},'language_info':{'name':'python','version':'3.12'}}
nbf.validate(nb);nbf.write(nb,BASE/'09_english_240_triplets.ipynb')
print('Built 09_english_240_triplets.ipynb')
