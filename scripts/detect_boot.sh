#!/bin/bash
#
# Script de detecção de tipo de boot para Calamares (bash)
# Uso: ./detect_boot.sh
#

detect_boot_type() {
    # Verifica se /sys/firmware/efi existe (indica UEFI)
    if [ -d /sys/firmware/efi ]; then
        echo "uefi"
    else
        echo "bios"
    fi
}

get_esp_mount() {
    # Procura partição EFI montada
    mount | grep -i 'esp\|efi' | awk '{print $3}' | head -1
}

check_secure_boot() {
    # Verifica Secure Boot
    if command -v mokutil &> /dev/null; then
        mokutil --sb-state 2>/dev/null | grep -i "enabled" && echo "enabled" || echo "disabled"
    elif [ -d /sys/firmware/efi/efivars ]; then
        # Verifica SecureBoot var
        if ls /sys/firmware/efi/efivars/ | grep -q "SecureBoot"; then
            echo "possibly_enabled"
        fi
    fi
    echo "unknown"
}

# Main
echo "========================================"
echo "Detecção de Boot - Calamares"
echo "========================================"
echo ""

BOOT_TYPE=$(detect_boot_type)
echo "Tipo de boot: $BOOT_TYPE"

if [ "$BOOT_TYPE" = "uefi" ]; then
    ESP=$(get_esp_mount)
    if [ -n "$ESP" ]; then
        echo "Partição ESP: $ESP"
    fi
    
    SB=$(check_secure_boot)
    echo "Secure Boot: $SB"
    
    # Informações adicionais
    if [ -f /sys/firmware/efi/fw_platform_size ]; then
        ARCH=$(cat /sys/firmware/efi/fw_platform_size)
        echo "Arquitetura EFI: ${ARCH}-bit"
    fi
else
    echo "Modo BIOS/Legacy detectado"
fi

echo ""
echo "========================================"

# Retorna código
if [ "$BOOT_TYPE" = "uefi" ]; then
    exit 0
else
    exit 1
fi
