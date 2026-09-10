"""Generate the post-score narrative from complete saved tables."""
import hashlib
import json
import shutil
import nbformat
import pandas as pd
from experiment import BASE,DATA,RESULTS,verify_freeze

verify_freeze()
s=pd.read_csv(RESULTS/'summary.csv').set_index('method')
ci=pd.read_csv(RESULTS/'intervals.csv')
random=pd.read_csv(RESULTS/'random_distributions.csv')
assert len(random)==4 and random.n_maps.eq(30).all()
assert set(zip(random.family,random.blend))=={(f,b) for f in ['gaussian','spectrum_matched'] for b in ['projection','hybrid50']}
control_runs=pd.read_csv(RESULTS/'random_summary.csv')
assert len(control_runs)==120 and not control_runs.duplicated(['family','replicate','blend']).any()
env=json.loads((RESULTS/'environment.json').read_text())
primary=ci[(ci.method=='hybrid50')&(ci.baseline=='embedding')&(ci.grouping=='conflict_and_topic')&(ci.metric=='accuracy')].iloc[0]
concept_ci=ci[(ci.method=='concept207')&(ci.baseline=='embedding')&(ci.grouping=='conflict_and_topic')&(ci.metric=='accuracy')].iloc[0]
practical=bool(primary.difference>=.05-1e-12 and primary.low>0)
specific=bool(random[random.blend.eq('hybrid50')].accuracy_p95.lt(s.loc['hybrid50','accuracy']).all())
def table(headers,records):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in records])
methods=['embedding','concept207','hybrid50']
main_table=table(['Метод','Правильно / 240','Accuracy','Δ к embedding'],
 [[m,f'{s.loc[m,"correct_score"]:g}/240',f'{s.loc[m,"accuracy"]:.2%}',f'{100*(s.loc[m,"accuracy"]-s.loc["embedding","accuracy"]):+.2f} п.п.'] for m in methods])
ci_table=table(['Сравнение','Группировка','Разность, п.п.','95% интервал, п.п.'],
 [[r.method+' − '+r.baseline,r.grouping,f'{100*r.difference:+.2f}',f'[{100*r.low:+.2f}; {100*r.high:+.2f}]'] for r in ci[ci.metric.eq('accuracy')].itertuples()])
control_table=table(['Карта','Использование','Min / median / p95 / max accuracy','Лучше концепт-аналога','Наравне'],
 [[r.family,r.blend,' / '.join(f'{getattr(r,"accuracy_"+x):.1%}' for x in ['min','median','p95','max']),f'{r.n_accuracy_strictly_above_concept}/30',f'{r.n_accuracy_equal_concept}/30'] for r in random.itertuples()])
trans=pd.read_csv(RESULTS/'transitions.csv')
transition_table=table(['Метод против baseline','Исправлено','Новых ошибок','Без смены балла'],
 [[r.method+' − '+r.baseline,r.improved_triplets,r.worsened_triplets,r.unchanged_triplets] for r in trans.itertuples()])
sens=pd.read_csv(RESULTS/'agreed_audit_sensitivity.csv')
initial_sens=pd.read_csv(RESULTS/'initial_audit_sensitivity.csv')
initial_sensitivity_table=table(['Метод','Согласованных троек по первым ответам','Accuracy'],
 [[r.method,r.n_triplets,f'{r.accuracy:.2%}'] for r in initial_sens.itertuples()])
alignment=[json.loads((DATA/f'audit_labels_{i}.json').read_text()) for i in [1,2]]
alignment_changes=[sum(r.get('alignment_changed',False) for r in audit) for audit in alignment]
alignment_unresolved=[sum(r.get('alignment_unresolved',False) for r in audit) for audit in alignment]
sensitivity_table=table(['Метод','Согласованных троек','Accuracy','Покрытие конфликтов / тем','Порог покрытия соблюдён'],
 [[r.method,r.n_triplets,f'{r.accuracy:.2%}',f'{r.n_conflicts} / {r.n_topics}',str(r.interpretable)] for r in sens.itertuples()])
loo=pd.read_csv(RESULTS/'leave_one_author_out.csv');loo_primary=loo[(loo.method=='hybrid50')&(loo.baseline=='embedding')]
by_conflict=pd.read_csv(RESULTS/'by_conflict.csv').pivot(index='conflict',columns='method',values='accuracy')
conflict_table=table(['Конфликт (20 троек)','Embedding','Concept207','Hybrid50','Δ смеси, п.п.'],
 [[k,f'{r.embedding:.0%}',f'{r.concept207:.0%}',f'{r.hybrid50:.0%}',f'{100*(r.hybrid50-r.embedding):+.0f}'] for k,r in by_conflict.iterrows()])
conflict_delta=by_conflict.hybrid50-by_conflict.embedding
intro=f"""На **240 новых английских тройках (720 уникальных абзацев)** обычный embedding дал **{s.loc['embedding','correct_score']:g}/240 ({s.loc['embedding','accuracy']:.2%})**, concept207 — **{s.loc['concept207','correct_score']:g}/240 ({s.loc['concept207','accuracy']:.2%})**, hybrid50 — **{s.loc['hybrid50','correct_score']:g}/240 ({s.loc['hybrid50','accuracy']:.2%})**.

Главная разность **hybrid50 − embedding = {100*primary.difference:+.2f} п.п.**, описательный двухфакторный 95% интервал **[{100*primary.low:+.2f}; {100*primary.high:+.2f}] п.п.** Рабочий ориентир «не менее +5 п.п. и нижняя граница выше нуля» **{'достигнут' if practical else 'не достигнут'}**. Модель — та же, что указана в Dilemma: **multilingual MiniLM, 384D**."""
random_statement=("Смесь с концептами превысила 95-й percentile обеих случайных контрольных семей по заранее заданному описательному сравнению. Это ограниченный результат на выбранных картах и корпусе, а не p-value или доказательство механизма." if specific else
 "Смесь с концептами не превысила 95-й percentile обеих случайных контрольных семей. По этому заранее заданному описательному критерию специфическое преимущество выбранных концептов над случайной переориентацией не установлено.")
report=f"""# English conflict-over-topic: 240 троек на модели Dilemma

{intro}

Заранее предусмотренный второй контраст, **concept207 − embedding**, равен **{100*concept_ci.difference:+.2f} п.п.**, его описательный 95% интервал — **[{100*concept_ci.low:+.2f}; {100*concept_ci.high:+.2f}] п.п.** Чистый профиль ошибается в **{240-s.loc['concept207','correct_score']:g}/240** случаях. Поэтому результат показывает измеримое улучшение на этом корпусе при всё ещё ограниченной абсолютной точности.

## Что зафиксировали до результата

Пользователь выбрал 240 троек и два AI-аудита до scoring. Все тексты написаны сразу на английском; это новый набор, без переводов прежних девяти абзацев и без повторного использования текстов между тройками. Конструкция каждой тройки: A — исходная дилемма, B — другой сюжет с тем же предполагаемым конфликтом, C — похожая тема при другом конфликте. Желаемая связь — **d(A,B)<d(A,C)**.

12 конфликтов × 10 anchor-тем × 2 варианта = 240. Для каждого конфликта 20 троек, каждой темы — 24. Детерминированная схема покрывает все направленные пары разных тем и конфликтов, сохраняя баланс ролей; определения и назначения опубликованы. Четыре авторские последовательности по 60 троек, сбалансированные по конфликту и теме. Это 240 уникальных троек, но не 240 гарантированно независимых человеческих наблюдений.

Первый проход крупных заданий дешёвыми AI-авторами отклонён до embeddings: встречались шаблоны, буквальные названия ценностей вместо событий и несогласованная грамматика. Окончательные тексты созданы gpt-5.6-sol частями по 12 троек с индивидуально написанными историями. Изменение процедуры раскрыто в [поправке до scoring](PRE_SCORE_AMENDMENT.md); исходный протокол и первая фиксация сохранены. Метрики, назначенные роли, модель и вес смеси не менялись по результатам.

Тексты имеют 40–70 слов; фактическая максимальная длина encoder — **{max(env['token_lengths'])} токенов** при лимите 128. Ни один текст не обрезан. Названия классов, роли, темы и аудиторские ответы не передаются encoder.

## Какая именно модель и что означает размерность

В сервисах анализа и поиска Dilemma по умолчанию задана `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; `hidden_size` и metadata атрибутов равны **384**. Python-исследование использует прежнюю закреплённую revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`, masked mean pooling и L2-нормировку. Config и tokenizer.json совпадают с папкой приложения. Различия обвязки раскрыты в протоколе; побитовое равенство Swift runtime не заявляется. Это проверка геометрии на той же модели, а не запуск всего pipeline извлечения reasons приложения.

384 — размер выходного sentence embedding, а не число слоёв модели. После перехода на фиксированные 207 прототипов получаем 207 координат профиля; у конкатенированной смеси — 384+207=**591**. Большая размерность сама по себе не означает лучшее качество.

От [Bhatia et al., PNAS, 2025](https://doi.org/10.1073/pnas.2406489122) взят банк описаний 207 атрибутов. Прежний код проекта усредняет нормированные embeddings фраз отдельно для pro/con, нормирует два прототипа, затем нормирует их сумму. Это наша адаптация к релевантности атрибута независимо от знака. Она не воспроизводит полную процедуру статьи: причины конкретных дилемм здесь не извлекаются. Размер 384, mean pooling и лимит 128 также указаны в [карточке MiniLM](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2); соответствие настройке Dilemma проверено отдельно по локальным исходникам.

Пусть z — нормированный embedding, A — прежняя карта 207 нормированных атрибутов. Тогда `c=norm(z @ (A−mean_rows(A)).T)`. Для смеси `h=[sqrt(0.5)z; sqrt(0.5)c]`; её cosine distance равна среднему двух исходных расстояний. Нет обучения или подбора веса. Карта детерминированно меняет геометрию уже имеющейся информации, не добавляя новую метку извне.

## Основной результат и ошибки

Accuracy — доля правильных предпочтений конфликта перед темой, точное равенство получает 0.5. Главный контраст заранее выбран как hybrid50 − embedding. Ориентир +5 п.п. предложен ассистентом и принят как допущение после прерванного вопроса; он **не выдаётся за явный выбор пользователя**.

{main_table}

{transition_table}

Последняя таблица показывает, сколько отдельных ошибок исправлено и сколько новых появилось; по одной итоговой accuracy этого не видно. Все расстояния AB/AC и `margin=d(A,C)−d(A,B)` доступны по каждой тройке. Средний margin вторичен: разные пространства не дают общей калиброванной шкалы уверенности.

## Неопределённость

10 000 двухфакторных парных bootstrap-перевзвешиваний: независимо выбираются с возвращением 12 конфликтов и 10 тем, оба варианта каждой клетки сохраняются. Дополнительно — отдельные группировки по каждому фактору. Это описательная устойчивость выбранной синтетической сетки, а не population CI для естественных пользовательских дилемм. Пересэмплирование не устраняет зависимость общей AI-модели и схемы задания.

{ci_table}

При исключении по одному из четырёх авторов разность hybrid50 − embedding находится в диапазоне **[{100*loo_primary.accuracy_difference.min():+.2f}; {100*loo_primary.accuracy_difference.max():+.2f}] п.п.** Все четыре оценки опубликованы в `results/leave_one_author_out.csv`. Выводы не выбираются по наиболее выгодному автору или типу конфликта.

Смесь улучшает точность в **{int(conflict_delta.gt(0).sum())}/12** классах, ухудшает в **{int(conflict_delta.lt(0).sum())}/12**, даёт тот же балл в **{int(conflict_delta.eq(0).sum())}/12**. В каждом классе всего 20 троек; эти срезы описательны.

{conflict_table}

Средние по каждой anchor-теме и автору также опубликованы в `results/by_anchor_topic.csv` и `results/by_author.csv`.

## Два аудита без авторских ролей

Каждый аудитор видел A/X/Y, случайные ID и инструкцию сравнивать основные конкурирующие ставки; B/C, авторские классы, темы и модели скрыты. В каждом входе правильный по автору кандидат находился на X ровно 120 раз, на Y — 120 раз. Допускались both и neither.

В первых ответах Luna обнаружились ошибки соответствия букв их же объяснениям; иногда `both` фактически обозначало A и один кандидат. Первые версии сохранены: согласия с автором **{env['initial_audit_agreements'][0]}/240** и **{env['initial_audit_agreements'][1]}/240**, совместно **{env['initial_both_audits_agree_count']}/240**. Попытка самопроверки не устранила явные ошибки. Поэтому до scoring две отдельные задачи Sol сверили все первоначальные объяснения со своими кандидатами, не видя авторского ключа или другого аудита. Буква изменена в **{alignment_changes[0]}** и **{alignment_changes[1]}** ответах; неразрешёнными помечены **{alignment_unresolved[0]}** и **{alignment_unresolved[1]}**. Исходные объяснения сохранены дословно. Эта дополнительная процедура раскрыта в [уточнении до scoring](PRE_SCORE_AUDIT_REPAIR.md); она не выдаётся за ещё два независимых смысловых аудита.

Аудитор 1 согласился с исходным B в **{env['auditor_1_agrees_count']}/240**, аудитор 2 — в **{env['auditor_2_agrees_count']}/240**. Оба подтвердили B в **{env['both_audits_agree_count']}/240**. Совпавших нормализованных ответов двух аудиторов — **{env['auditors_same_normalized_choice_count']}/240**. Это отдельные AI-задания с общими модельными ограничениями, не независимая человеческая разметка.

В основной таблице сохранены все 240 исходных отношений. Заранее заявленная чувствительность ограничивается тройками, где оба аудитора выбрали B:

{sensitivity_table}

Она не заменяет основной итог. Для содержательной интерпретации заранее требовались не менее 120 троек, 8 конфликтов и 6 тем. Все разногласия и объяснения сохранены; после аудитов корпус не редактировался.

Чтобы показать влияние исправления кодирования, ниже тот же дополнительный расчёт по согласованию **первых** ответов. Этот поднабор содержит известные ошибки букв и не является альтернативным gold standard:

{initial_sensitivity_table}

## Контроль произвольной геометрии

30 Gaussian-карт в 207 координат и 30 случайных ориентаций с тем же спектром, что у концепт-карты, с seeds до scoring. Для каждой проверены отдельная проекция и смесь 50/50 с z. Случайные карты получают семантический embedding и потому не обязаны давать 50% accuracy.

{control_table}

{random_statement}

Для чистой проекции лучшая Gaussian-карта дала **{random[(random.family=='gaussian')&(random.blend=='projection')].accuracy_max.iloc[0]:.2%}**, лучшая карта с тем же спектром — **{random[(random.family=='spectrum_matched')&(random.blend=='projection')].accuracy_max.iloc[0]:.2%}**, concept207 — **{s.loc['concept207','accuracy']:.2%}**. Это позволяет отдельно оценить направления концептов, а не только наличие сжатия. В смеси число случайных карт, превысивших концепт-смесь, равно **{int(random[random.blend.eq('hybrid50')].n_accuracy_strictly_above_concept.sum())}/60**.

Число случайных карт не увеличивает число текстов или независимых датасетов. Доли превышений не являются p-values. Победа над обычным embedding и специфичность банка концептов — разные утверждения.

## Пределы выводов и материалы

Эксперимент проверяет различение конфликтов на новой конструктивной AI-синтетике с известными автору классами. Лексические подсказки, ограничения двенадцати определений, общие авторские инструкции и перекрывающиеся ценности остаются. Результат не доказывает понимания абстрактных конфликтов, универсальности concept layers или качества на естественных обращениях. Человеческая валидация в этом запуске отсутствует. По сравнению с прежними тремя русскими тройками изменились одновременно язык, размер и формулировки корпуса; разницу результатов нельзя приписывать только переходу на английский.

Готовы [исполненный notebook](09_english_240_triplets.ipynb), [исходный корпус](data/triplets.json), [протокол](PROTOCOL.md), [все основные оценки](results/per_triplet.csv), [интервалы](results/intervals.csv), [случайные контроли](results/random_summary.csv), [независимый пересчёт](reports/numeric_audit.md). Инструкции воспроизведения — [README.md](README.md); `verification.json` содержит проверки и хеши. Отчёты авторских частей и обоих аудиторов сохранены в `reports/`. Предыдущие исследования не изменены.
"""
(BASE/'research_note.md').write_text(report)
pure_above=int(random[random.blend.eq('projection')].n_accuracy_strictly_above_concept.sum())
pure_equal=int(random[random.blend.eq('projection')].n_accuracy_equal_concept.sum())
hybrid_above=int(random[random.blend.eq('hybrid50')].n_accuracy_strictly_above_concept.sum())
control_abstract=("The concept profile exceeded all 30 Gaussian and all 30 spectrum-matched pure projections on this corpus." if pure_above+pure_equal==0 else f"Among 60 random pure projections, {pure_above} exceeded and {pure_equal} tied the concept profile.")
abstract=f"""# Research abstract: conflict-sensitive retrieval in a fixed embedding space

We evaluated whether a fixed concept-derived geometry helps prioritize a shared decision conflict over shared topic. The dataset contains 240 newly authored English triplets (720 unique paragraphs), balanced across 12 conflict classes and 10 anchor topics. Each query is paired with a same-conflict candidate from another topic and a same-topic candidate with a different conflict. The encoder is Dilemma's configured paraphrase-multilingual-MiniLM-L12-v2 (384 dimensions). We compared cosine distance in the original embedding, a centered 207-attribute concept profile, and their fixed 50/50 mixture, without training or weight selection.

Original embeddings achieved {s.loc['embedding','accuracy']:.2%} accuracy, concept profiles {s.loc['concept207','accuracy']:.2%}, and the mixture {s.loc['hybrid50','accuracy']:.2%}. The prespecified main contrast (mixture minus embedding) was {100*primary.difference:+.2f} percentage points, with a descriptive paired two-factor bootstrap interval of [{100*primary.low:+.2f}, {100*primary.high:+.2f}] percentage points. The prespecified secondary concept-minus-embedding contrast was {100*concept_ci.difference:+.2f} points [{100*concept_ci.low:+.2f}, {100*concept_ci.high:+.2f}]. {control_abstract} Random mixtures exceeding the concept mixture: {hybrid_above}/60. These are descriptive controls, not independent datasets or p-values.

Two masked AI audits jointly agreed with the authored preference on {env['both_audits_agree_count']} of 240 triplets after separate masked checks for inconsistencies between candidate letters and the original explanations. Initial joint agreement was {env['initial_both_audits_agree_count']}/240. Both initial and corrected audit sensitivities are retained; all 240 authored relations define the primary outcome.

The dataset, code, and audits were prepared with AI assistance. This is a synthetic pilot, without blinded human relevance judgments; the interval describes sensitivity within the constructed grid and is not a population confidence interval. All outcomes and controls are reported, including failures. The experiment distinguishes baseline improvement from concept-specific advantage and does not establish a universal property of embeddings.
"""
(BASE/'abstract_en.md').write_text(abstract)
source=BASE.parents[1]/'reports/concept_layers_large_en'
(BASE/'reports').mkdir(exist_ok=True)
for p in source.glob('*'):
    if p.suffix in {'.md','.py','.json'}:shutil.copy2(p,BASE/'reports'/p.name)
notebook=BASE/'09_english_240_triplets.ipynb'
nb=nbformat.read(notebook,as_version=4)
before=[hashlib.sha256(c.source.encode()).hexdigest() for c in nb.cells if c.cell_type=='code']
nb.cells=[c for c in nb.cells if not c.metadata.get('post_score_summary')]
cell=nbformat.v4.new_markdown_cell('## Полученный результат\n\n'+intro+'\n\n'+random_statement)
cell.metadata['post_score_summary']=True;nb.cells.insert(1,cell)
assert before==[hashlib.sha256(c.source.encode()).hexdigest() for c in nb.cells if c.cell_type=='code']
nbformat.validate(nb);nbformat.write(nb,notebook)
print('Wrote readable report, English abstract and post-score notebook summary.')
