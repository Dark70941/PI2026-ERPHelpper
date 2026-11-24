#!/bin/bash
# ==============================================================================
# Script de Restore e Recuperação de Desastres (AWS Production Readiness)
# ==============================================================================
# Este script restaura a base vetorial do ChromaDB a partir do último backup
# armazenado no Amazon S3 (ou de um arquivo específico passado por parâmetro).
# ==============================================================================

set -euo pipefail

S3_BUCKET="${BACKUP_S3_BUCKET:-erp-helpper-backups}"
APP_DIR="${APP_DIR:-/app}"
RESTORE_TMP="/tmp/restore_db"
BACKUP_SPECIFIC="${1:-}"

echo "=========================================================="
echo " [RESTORE] Iniciando procedimento de restauração de dados"
echo " [RESTORE] Horário: $(date)"
echo "=========================================================="

mkdir -p "${RESTORE_TMP}"

if [ -z "${BACKUP_SPECIFIC}" ]; then
    echo "[1/4] Buscando o backup mais recente no S3..."
    LATEST_BACKUP=$(aws s3 ls "s3://${S3_BUCKET}/backups/" | sort | tail -n 1 | awk '{print $4}')
    if [ -z "${LATEST_BACKUP}" ]; then
        echo "❌ Nenhum arquivo de backup encontrado no bucket s3://${S3_BUCKET}/backups/"
        exit 1
    fi
    echo "Arquivo selecionado: ${LATEST_BACKUP}"
    S3_SOURCE="s3://${S3_BUCKET}/backups/${LATEST_BACKUP}"
    LOCAL_TAR="${RESTORE_TMP}/${LATEST_BACKUP}"
else
    echo "[1/4] Usando backup especificado: ${BACKUP_SPECIFIC}"
    S3_SOURCE="s3://${S3_BUCKET}/backups/${BACKUP_SPECIFIC}"
    LOCAL_TAR="${RESTORE_TMP}/${BACKUP_SPECIFIC}"
fi

echo "[2/4] Baixando backup do Amazon S3..."
aws s3 cp "${S3_SOURCE}" "${LOCAL_TAR}"

echo "[3/4] Descompactando e restaurando base vetorial..."
tar -xzf "${LOCAL_TAR}" -C "${APP_DIR}"

echo "[4/4] Validando integridade da restauração..."
if [ -d "${APP_DIR}/base_de_conhecimento_db" ] && [ -f "${APP_DIR}/knowledge_base.json" ]; then
    echo "✅ Diretórios e arquivos de conhecimento restaurados com sucesso!"
else
    echo "❌ Falha na restauração dos diretórios esperados."
    exit 1
fi

rm -rf "${RESTORE_TMP}"

echo "=========================================================="
echo " [RESTORE] Restauração concluída com sucesso!"
echo " Dica: Reinicie o container com: docker compose restart"
echo " E valide com: python test_api.py health"
echo "=========================================================="
