# English conflict-over-topic: 240 троек

[Читаемый отчёт](research_note.md), [исполненный notebook](09_english_240_triplets.ipynb), [английский abstract](abstract_en.md).

[Навигация по всем исследовательским веткам](reports/INDEX.md): авторы, два смысловых аудитора, проверка метода и независимый численный пересчёт.

720 новых английских абзацев; модель Dilemma `paraphrase-multilingual-MiniLM-L12-v2`, 384D. Сравнение исходного embedding, фиксированного концепт-профиля207 и смеси50/50. Два маскированных AI-аудита и 60 случайных карт. Человеческой валидации в этом опыте нет.

## Воспроизведение

Из корня проекта:

```bash
.venv/bin/python notebooks/concept_layers_large_en/check_metrics.py
.venv/bin/python notebooks/concept_layers_large_en/execute_notebook.py
.venv/bin/python notebooks/concept_layers_large_en/write_report.py
```

Для отдельного распакованного пакета, находясь в его папке:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python check_metrics.py
.venv/bin/python execute_notebook.py
.venv/bin/python write_report.py
.venv/bin/python reports/independent_recheck.py .
```

CPU, без платных API. Интернет нужен только для первого скачивания публичной модели, если локального кеша нет; revision зафиксирована. Для независимого пересчёта encoder не нужен: используются сохранённые основные векторы, прежняя карта и seeds случайных проекций. Копии всех случайных векторов в архив не включаются: они детерминированно восстанавливаются из этих входов, что уменьшает пакет.

`experiment.py` проверяет SHA256 входов и отказывается запускать изменённый опыт как прежний. `make_corpus.py` — журналируемая сборка до аудитов; не запускать её для пересчёта уже зафиксированного результата. Для восстановления пустого notebook есть `build_notebook.py`; затем notebook нужно исполнить и вызвать `write_report.py`. Научные code cells сохраняются при добавлении выводов после scores.

## Данные и происхождение

- `PROTOCOL.md` и `data/design_manifest.json` — дизайн до генерации; `PRE_SCORE_AMENDMENT.md` — открытая поправка о пересоздании шаблонного первого прохода до scoring.
- `PRE_SCORE_AUDIT_REPAIR.md` — дополнительная проверка соответствия букв исходным объяснениям аудиторов; первые версии и неудачная промежуточная попытка сохранены в `data/audit_initial/` и `data/audit_alignment_attempt/`.
- `data/triplets.json` — 240 окончательных троек. Части авторов и назначения сохраняют происхождение каждого текста.
- `data/audit_input_*.json`, `audit_key_*.json`, `audit_labels_*.json` — маскированные входы двух аудиторов, закрытые от них ключи и исходные ответы. Эти файлы не передаются encoder.
- `data/frozen_manifest.json` — фиксация окончательных научных входов до scoring.
- `results/per_triplet.csv` — 720 основных оценок; `random_per_triplet.csv` — 28 800 контрольных; `intervals.csv` — все заранее заявленные парные интервалы.
- `results/initial_audit_sensitivity.csv` — чувствительность по согласованию первых ответов, чтобы раскрыть влияние последующего исправления букв.
- `results/main_vectors.npz`, `random_map_specs.json`, `environment.json` — независимый пересчёт без модели.
- `reports/` — отчёты всех авторских частей, аудиторов и численного проверяющего. Отчёты отклонённого первого прохода явно помечены `rejected_`.
- `verification.json` — выполненные проверки и хеши итоговых артефактов.

Сырые отклонённые генерации остаются отдельно в исходном репозитории и не входят в архив; их отчёты и объяснение отклонения сохранены. Кеши, веса модели и окружение также не включены. Прежние эксперименты не нужны для воспроизведения: численная карта скопирована в пакет.
