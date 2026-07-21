from __future__ import annotations

from pathlib import Path

import yaml

from instream_rules.dsl import RuleDefinition


def load_rules_from_dir(directory: str | Path) -> list[RuleDefinition]:
    """Load every `*.yaml` rule definition in a customer pack's `rules/` folder.

    This is how a pack's authored rules get turned into `RuleDefinition`
    objects for the engine — and, separately, into `Rule`/`RuleVersion` DB
    rows when a pack is installed/published via the `/rules` API.
    """
    path = Path(directory)
    rules: list[RuleDefinition] = []
    for file in sorted(path.glob("*.yaml")):
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
        rules.append(RuleDefinition.model_validate(data))
    return rules
