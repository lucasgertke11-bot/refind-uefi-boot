#!/usr/bin/env python3
"""
Script de detecção de tipo de boot para Calamares
Detecta automaticamente se o sistema usa UEFI ou BIOS
"""

import os
import subprocess
import sys

def detect_boot_type():
    """
    Detecta o tipo de boot do sistema
    Retorna: 'uefi' ou 'bios'
    """
    
    # Método 1: Verificar /sys/firmware/efi (mais confiável)
    if os.path.exists('/sys/firmware/efi'):
        return "uefi"
    
    # Método 2: Tentar usar efivar (se disponível)
    try:
        result = subprocess.run(
            ['efivar', '-l'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return "uefi"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Método 3: Verificar mountpoint da partição EFI
    try:
        result = subprocess.run(
            ['mount'],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if 'esp' in line.lower() or ' efi ' in line.lower():
                return "uefi"
    except:
        pass
    
    # Se nenhum método indicar UEFI, assume BIOS
    return "bios"

def detect_uefi_firmware_info():
    """
    Retorna informações sobre o firmware UEFI
    """
    info = {
        "efivars": os.path.exists('/sys/firmware/efi/efivars'),
        "fw_platform_size": None,
        "firmware_vendor": None,
    }
    
    # Tentar ler informações do firmware
    fw_size_path = '/sys/firmware/efi/fw_platform_size'
    if os.path.exists(fw_size_path):
        try:
            with open(fw_size_path, 'r') as f:
                info["fw_platform_size"] = f.read().strip()
        except:
            pass
    
    return info

def get_esp_mountpoint():
    """
    Retorna o ponto de montagem da partição ESP
    """
    try:
        result = subprocess.run(
            ['mount'],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if 'esp' in line.lower() or ('efi' in line.lower() and '/boot/efi' in line):
                parts = line.split()
                if len(parts) >= 3:
                    return parts[2]
    except:
        pass
    return None

def check_secure_boot():
    """
    Verifica se Secure Boot está habilitado
    """
    try:
        # Método 1: Verificar mokutil
        result = subprocess.run(
            ['mokutil', '--sb-state'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            if "enabled" in result.stdout.lower():
                return True
            return False
    except FileNotFoundError:
        pass
    
    # Método 2: Verificar efivars
    try:
        if os.path.exists('/sys/firmware/efi/efivars/SecureBoot-*'):
            return True
    except:
        pass
    
    return None  # Desconhecido

def main():
    print("=" * 50)
    print("Detecção de Boot - Script para Calamares")
    print("=" * 50)
    print()
    
    boot_type = detect_boot_type()
    print(f"Tipo de boot detectado: {boot_type.upper()}")
    print()
    
    # Informações adicionais
    if boot_type == "uefi":
        uefi_info = detect_uefi_firmware_info()
        print(f"EFI Vars: {'Sim' if uefi_info['efivars'] else 'Não'}")
        if uefi_info['fw_platform_size']:
            print(f"Plataforma: {uefi_info['fw_platform_size']} bits")
        
        esp = get_esp_mountpoint()
        if esp:
            print(f"ESP montada em: {esp}")
        
        sb = check_secure_boot()
        if sb is not None:
            print(f"Secure Boot: {'Ativado' if sb else 'Desativado'}")
    else:
        print("Sistema booted em modo BIOS/Legacy")
    
    print()
    print("=" * 50)
    
    # Retornar código para uso em shell
    return 0 if boot_type == "uefi" else 1

if __name__ == "__main__":
    sys.exit(main())
