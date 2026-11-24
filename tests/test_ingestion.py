"""
test_ingestion.py - Testes Unitários para as Funções de Chunking e Normalização de Dados
"""

import unittest
import tests.mock_helper  # Garante mocks de dependências se não instaladas
from main import chunk_text_with_overlap, _normalizar_documento


class TestIngestion(unittest.TestCase):

    def test_chunk_text_empty(self):
        """Texto vazio ou nulo deve retornar lista vazia."""
        self.assertEqual(chunk_text_with_overlap(""), [])
        self.assertEqual(chunk_text_with_overlap(None), [])

    def test_chunk_text_within_limit(self):
        """Texto curto deve retornar um único chunk."""
        texto = "Este é um texto curto para teste de chunking."
        chunks = chunk_text_with_overlap(texto, max_tokens=100, overlap=20)
        self.assertEqual(len(chunks), 1)

    def test_chunk_text_invalid_overlap(self):
        """Overlap maior ou igual a max_tokens deve lançar ValueError."""
        with self.assertRaises(ValueError):
            chunk_text_with_overlap("Texto de teste", max_tokens=50, overlap=50)

    def test_normalizar_documento_completo(self):
        """Documento com todos os campos deve ser normalizado corretamente."""
        doc_raw = {
            "Categoria": "Fiscal",
            "Titulo": "Rejeição 201",
            "Conteudo": "Duplicidade de NF-e na SEFAZ",
            "Palavras Chave": "nfe, 201",
            "URL": "https://wiki.erp-exemplo.com.br/artigo/201"
        }
        norm = _normalizar_documento(doc_raw, 42)
        self.assertEqual(norm["document_id"], "42")
        self.assertEqual(norm["category"], "Fiscal")
        self.assertEqual(norm["title"], "Rejeição 201")
        self.assertEqual(norm["full_text"], "Duplicidade de NF-e na SEFAZ")
        self.assertEqual(norm["keywords"], "nfe, 201")
        self.assertEqual(norm["source_url"], "https://wiki.erp-exemplo.com.br/artigo/201")
        self.assertIn("Título: Rejeição 201", norm["texto_embedding"])

    def test_normalizar_documento_campos_vazios(self):
        """Documento com campos ausentes deve preencher strings vazias sem falhar."""
        doc_raw = {}
        norm = _normalizar_documento(doc_raw, 0)
        self.assertEqual(norm["document_id"], "0")
        self.assertEqual(norm["category"], "")
        self.assertEqual(norm["title"], "")
        self.assertEqual(norm["full_text"], "")
        self.assertEqual(norm["keywords"], "")


if __name__ == "__main__":
    unittest.main()
