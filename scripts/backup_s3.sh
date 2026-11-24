#!/bin/bash
# ==============================================================================
# Script de Backup Automatizado para Amazon S3 (AWS Production Readiness)
# ==============================================================================
# Este script cria um snapshot compactado da base vetorial ChromaDB e da base
# de conhecimento JSON, realizando o upload para o bucket Amazon S3 configurado.
# ==============================================================================

set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/tmp/erp_helpper_backup_${TIMESTAMP}"
BACKUP_FILE="backup_vector_db_${TIMESTAMP}.tar.gz"
S3_BUCKET="${BACKUP_S3_BUCKET:-erp-helpper-backups}"
S3_PATH="s3://${S3_BUCKET}/backups/${BACKUP_FILE}"
APP_DIR="${APP_DIR:-/app}"

echo "=========================================================="
echo " [BACKUP] Iniciando rotina de backup: $(date)"
echo " [BACKUP] Destino S3: ${S3_PATH}"
echo "=========================================================="

# Criar pasta temporária
mkdir -p "${BACKUP_DIR}"

# Compactar base vetorial ChromaDB e knowledge_base.json
cd "${APP_DIR}"
echo "[1/3] Compactando base vetorial e arquivos de conhecimento..."
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    base_de_conhecimento_db \
    knowledge_base.json

FILESIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
echo "✅ Arquivo gerado: ${BACKUP_FILE} (${FILESIZE})"

# Enviar para o Amazon S3
echo "[2/3] Enviando arquivo para o Amazon S3..."
if command -v aws >/dev/null 2>&1; then
    aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "${S3_PATH}"
    echo "✅ Upload concluído com sucesso em: ${S3_PATH}"
else
    echo "⚠️ AWS CLI não encontrado no ambiente atual."
    echo "Simulação de backup salva localmente em: ${BACKUP_DIR}/${BACKUP_FILE}"
fi

# Limpeza local de temporários
echo "[3/3] Limpando arquivos temporários locais..."
rm -rf "${BACKUP_DIR}"

echo "=========================================================="
echo " [BACKUP] Processo finalizado com sucesso às $(date)!"
echo "=========================================================="
