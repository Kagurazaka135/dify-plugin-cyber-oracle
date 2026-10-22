# Privacy Policy

Cyber Oracle (赛博神棍) is a divination tool plugin for Dify.

- **Casting is local.** All seven divination methods are deterministic pure
  computation performed inside the plugin process. No casting data is uploaded
  to any third party by the plugin itself.
- **No API keys.** The plugin does not require, store, or transmit any LLM API
  key. It contains no network client of its own.
- **Optional AI interpretation.** When you enable AI interpretation and select
  a model, the plugin reverse-invokes the LLM configured in **your own Dify
  workspace**. In that case the casting result and your question are processed
  by that model under your workspace's own provider settings and terms.
- **No telemetry.** The plugin collects no usage statistics and adds no
  tracking of any kind.
- **Data files.** The bundled JSON data files (hexagram texts, oracle poems,
  stroke counts) are static reference data shipped with the plugin; see
  `data/SOURCES.md` for their provenance and licenses.

**For entertainment only.** Divination results are not factual predictions.
