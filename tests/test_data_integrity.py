"""
test_data_integrity.py - Testes de Integridade Estrutural dos Arquivos de Dados e Configuração
"""

import unittest
import json
import os


class TestDataIntegrity(unittest.TestCase):

    def test_knowledge_base_json_exists_and_valid(self):
        """Garante que knowledge_base.json existe, é válido e possui estrutura correta."""
        file_path = "knowledge_base.json"
        self.assertTrue(os.path.exists(file_path), f"Arquivo {file_path} não encontrado.")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list, "knowledge_base.json deve ser uma lista de artigos.")
        self.assertGreater(len(data), 0, "knowledge_base.json não pode estar vazio.")

        campos_obrigatorios = {"Categoria", "Titulo", "Conteudo", "Palavras Chave", "URL"}
        for idx, item in enumerate(data):
            for campo in campos_obrigatorios:
                self.assertIn(campo, item, f"Artigo no índice {idx} não contém o campo '{campo}'.")

    def test_n8n_workflow_json_valid(self):
        """Garante que o workflow exportado do n8n possui nós e conexões válidas."""
        file_path = "n8n/workflow_uno_erp_helpper.json"
        self.assertTrue(os.path.exists(file_path), f"Arquivo {file_path} não encontrado.")

        with open(file_path, "r", encoding="utf-8") as f:
            wf = json.load(f)

        self.assertIn("nodes", wf, "Workflow do n8n precisa conter a chave 'nodes'.")
        self.assertGreater(len(wf["nodes"]), 0, "Workflow do n8n deve conter ao menos 1 nó.")

        # Verifica se há nós essenciais
        tipos_de_nos = [n.get("type", "") for n in wf["nodes"]]
        self.assertTrue(any("webhook" in t.lower() for t in tipos_de_nos), "Workflow deve conter nó do tipo Webhook.")
        self.assertTrue(any("code" in t.lower() for t in tipos_de_nos), "Workflow deve conter nó de código JavaScript.")

    def test_essential_files_present(self):
        """Verifica a presença de todos os arquivos essenciais de documentação e infraestrutura."""
        arquivos = [
            ".env.example",
            "index.html",
            "README.md",
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "cloudformation/aws-infrastructure.yaml",
            "scripts/backup_s3.sh",
            "scripts/restore_s3.sh",
            "scripts/load_test.py"
        ]
        for arq in arquivos:
            self.assertTrue(os.path.exists(arq), f"Arquivo essencial ausente: {arq}")


if __name__ == "__main__":
    unittest.main()
