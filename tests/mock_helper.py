"""
mock_helper.py - Garante que os testes unitários rodem em qualquer ambiente,
mesmo se as dependências externas pesadas (ex: chromadb, openai) não estiverem instaladas localmente.
"""

import sys
from unittest.mock import MagicMock

modulos_externos = ["openai", "chromadb", "tiktoken", "flask", "dotenv", "tqdm"]

for mod in modulos_externos:
    try:
        __import__(mod)
    except ImportError:
        mock = MagicMock()
        if mod == "tiktoken":
            # Mock específico do encoder de tokens
            enc = MagicMock()
            enc.encode.side_effect = lambda t: list(range(len(str(t).split())))
            enc.decode.side_effect = lambda tok: " ".join([f"palavra_{i}" for i in tok])
            mock.encoding_for_model.return_value = enc
        elif mod == "flask":
            # Mock básico do Flask para não quebrar a carga de rotas
            flask_app = MagicMock()
            flask_app.route.return_value = lambda f: f
            flask_app.test_client.return_value = MagicMock()
            mock.Flask.return_value = flask_app
            mock.request = MagicMock()
            mock.jsonify = lambda d: d
        sys.modules[mod] = mock
