# -*- coding: utf-8 -*-
"""Cyber Oracle tool provider: no credentials required."""

from typing import Any

from dify_plugin import ToolProvider


class CyberOracleProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        pass
