# Модель Dilemma: проверка источников в репозитории

В DecisionKernel/Sources/Core/DecisionAnalysisService.swift и DecisionSimilarityService.swift модель по умолчанию — `paraphrase-multilingual-MiniLM-L12-v2`. Метаданные `DecisionKernel/Resources/Attributes/attributes_multi_l12.json` содержат model ID `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` и embedding_dimension384. В config.json локальной модели hidden_size384; число слоёв12 — другая характеристика.

LocalEmbeddingRuntime.swift явно выполняет masked mean pooling последовательности токенов и L2-нормировку. Python-кеш используемой в предыдущих экспериментах revision e8f8c211226b894fcb81acc59f3b34ba3efd5f42 содержит то же описание mean pooling. Config.json, tokenizer.json и special_tokens_map.json побитово совпадают с папкой приложения. Tokenizer_config различается полем tokenizer_class: Swift-совместимая папка указывает XLMRobertaTokenizer, Python — PreTrainedTokenizerFast.

В папке модели приложения текущего checkout лежат config и tokenizer-файлы, но нет весов. Для исследования доступны локальные pinned-веса Hugging Face; их SHA256 записывается в provenance. Поэтому заявляется та же модель и аналогичная схема pooling, но не побитовая эквивалентность всего Swift runtime. Изменения кода или модели приложения в рамках исследования не выполняются.

Swift tokenizer допускает maxLength512; SentenceTransformers конфигурация —128. Корпус должен целиком помещаться в128, что проверяется до scoring. Encoder исследования получает только английский исходный абзац; options, reasons, классы и аудиторские метки ему не передаются.

Основной embedding имеет384 координаты, концепт-профиль207, конкатенированная смесь591. Последние два представления детерминированно получены из первого и не содержат независимой информации, добавленной обучением на тесте.
# Дополнительная сверка первичных источников

9 сентября 2026 года повторно прочитана [карточка multilingual MiniLM](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2): 384-мерный выход, mean pooling и `max_seq_length=128`. Она согласуется с исследовательской Python-обвязкой; выбор этой модели в Dilemma подтверждается локальными исходниками, а не самой карточкой.

Источник словаря атрибутов: Bhatia, van Baal, Wang & Walasek (2025), [Computational analysis of 100 K choice dilemmas: Decision attributes, trade-off structures, and model-based prediction](https://doi.org/10.1073/pnas.2406489122). Статья использует 207 атрибутов для кодирования извлечённых причин. Здесь банк используется для собственной геометрической адаптации непосредственно абзацев, без извлечения причин и без переноса оценок точности статьи на текущий тест.
