"""
test_endpoints.py - Testes Unitários para as Rotas Flask (/health, / e /search)
"""

import unittest
import json
import tests.mock_helper  # Garante mocks de dependências se não instaladas
from unittest.mock import patch, MagicMock
from main import app, root, health, search


class TestEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_root_function(self):
        """A função root() deve retornar status UP e metadados da aplicação."""
        resp, status_code = root()
        self.assertEqual(status_code, 200)
        # Suporta tanto dicionário puro quanto objeto Response
        data = resp if isinstance(resp, dict) else (resp.get_json() if hasattr(resp, 'get_json') else resp)
        self.assertEqual(data["status"], "UP")
        self.assertEqual(data["service"], "erp-helpper-search-api")
        self.assertIn("endpoints", data)

    def test_health_function(self):
        """A função health() deve retornar status code 200 ou 503 e diagnóstico do banco."""
        resp, status_code = health()
        self.assertIn(status_code, [200, 503])
        data = resp if isinstance(resp, dict) else (resp.get_json() if hasattr(resp, 'get_json') else resp)
        self.assertIn("status", data)
        self.assertIn("version", data)
        self.assertIn("database", data)

    @patch("main.collection_global", None)
    def test_health_down_when_db_none(self):
        """Quando o banco for None, o health check deve indicar DOWN com código 503."""
        resp, status_code = health()
        self.assertEqual(status_code, 503)
        data = resp if isinstance(resp, dict) else (resp.get_json() if hasattr(resp, 'get_json') else resp)
        self.assertEqual(data["status"], "DOWN")

    @patch("main.collection_global", None)
    def test_search_fails_when_db_none(self):
        """A rota /search deve retornar 503 se o banco não estiver inicializado."""
        resp, status_code = search()
        self.assertEqual(status_code, 503)


if __name__ == "__main__":
    unittest.main()
