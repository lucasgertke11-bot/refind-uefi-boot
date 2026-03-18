# Bootloaders Universais para Linux

Este repositório contém bootloaders compilados para garantir compatibilidade total com qualquer sistema BIOS/UEFI.

## Estrutura

```
refind-uefi-boo/
├── grub/
│   ├── bios/          # GRUB para BIOS/Legacy
│   └── uefi/          # GRUB para UEFI
├── clover/
│   ├── bios/         # Clover para BIOS/Legacy (boot7)
│   └── uefi/         # Clover para UEFI (CLOVERX64.efi)
├── limine/
│   ├── bios/         # Limine para BIOS/Legacy
│   └── uefi/         # Limine para UEFI (BOOTX64.EFI)
├── scripts/          # Scripts para detecção e instalação
└── README.md
```

## Arquivos

### GRUB 2.12
| Arquivo | Uso |
|---------|-----|
| `grub-bios.img` | Imagem BIOS (compacta) |
| `grub-uefi.img` | Imagem UEFI (compacta) |
| `i386-pc/` | Módulos BIOS |
| `x86_64-efi/` | Módulos UEFI |

### Clover
| Arquivo | Uso |
|---------|-----|
| `CLOVERX64.efi` | Bootloader UEFI (para /EFI/BOOT/BOOTX64.EFI) |
| `BOOTX64.efi` | Cópia do Clover para boot UEFI |
| `boot7` | Bootloader BIOS/Legacy (para MBR) |

### Limine
| Arquivo | Uso |
|---------|-----|
| `BOOTX64.EFI` | Bootloader UEFI (para /EFI/BOOT/BOOTX64.EFI) |
| `limine-bios.sys` | Bootloader BIOS/Legacy (para MBR) |
| `limine-bios-hdd.bin` | Imagem BIOS para HD |

---

# Guia de Integração com Calamares

## Visão Geral

O Calamares pode detectar automaticamente o tipo de boot do PC e instalar o bootloader apropriado.

## Detecção do Tipo de Boot

### Método 1: Verificar sysfs (Recomendado)

```python
def detect_boot_type():
    """Detecta se o sistema boot em UEFI ou BIOS"""
    
    # Verifica se /sys/firmware/efi existe (indica UEFI)
    import os
    if os.path.exists('/sys/firmware/efi'):
        return "uefi"
    else:
        return "bios"
```

### Método 2: Usar efivar (Mais confiável)

```python
def detect_uefi():
    """Verifica variáveis EFI"""
    import subprocess
    try:
        result = subprocess.run(
            ['efivar', '-l'],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def detect_boot_type():
    if detect_uefi():
        return "uefi"
    else:
        return "bios"
```

### Método 3: Verificar mount point ESP

```python
def detect_boot_type():
    """Verifica partição ESP montada"""
    import subprocess
    try:
        result = subprocess.run(
            ['mount'],
            capture_output=True, text=True
        )
        if 'esp' in result.stdout.lower() or 'efi' in result.stdout.lower():
            return "uefi"
    except:
        pass
    return "bios"
```

---

## Instalação Automática

### Script de Instalação (bash)

```bash
#!/bin/bash

# detect_boot_type.sh
# Detecta o tipo de boot e instala o bootloader apropriado

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

detect_boot_type() {
    if [ -d /sys/firmware/efi ]; then
        echo "uefi"
    else
        echo "bios"
    fi
}

install_grub_uefi() {
    local target_dir="$1"
    echo -e "${GREEN}Instalando GRUB para UEFI...${NC}"
    
    # Copiar imagem EFI
    cp grub/uefi/*.img "$target_dir/"
    
    # Criar diretório EFI
    mkdir -p "$target_dir/EFI/Linux"
    mkdir -p "$target_dir/EFI/BOOT"
    
    # Copiar arquivos GRUB
    cp -r grub/uefi/x86_64-efi "$target_dir/EFI/BOOT/"
    
    echo "GRUB UEFI instalado em $target_dir/EFI/BOOT/"
}

install_grub_bios() {
    local target_disk="$1"
    echo -e "${GREEN}Instalando GRUB para BIOS...${NC}"
    
    # Instalar no MBR
    grub-install --boot-directory=/boot --target=i386-pc "$target_disk"
    
    echo "GRUB BIOS instalado em $target_disk"
}

install_clover_uefi() {
    local esp_mount="$1"
    echo -e "${GREEN}Instalando Clover para UEFI...${NC}"
    
    # Copiar Clover para partição ESP
    mkdir -p "$esp_mount/EFI/BOOT"
    cp clover/uefi/BOOTX64.efi "$esp_mount/EFI/BOOT/"
    cp clover/uefi/CLOVERX64.efi "$esp_mount/EFI/CLOVER/"
    
    echo "Clover UEFI instalado em $esp_mount/EFI/BOOT/"
}

install_clover_bios() {
    local target_disk="$1"
    echo -e "${GREEN}Instalando Clover para BIOS/Legacy...${NC}"
    
    # Copiar boot7 para o MBR
    dd if=clover/bios/boot7 of="$target_disk" bs=440 count=1 conv=notrunc
    
    echo "Clover BIOS instalado em $target_disk"
}

install_limine_uefi() {
    local esp_mount="$1"
    echo -e "${GREEN}Instalando Limine para UEFI...${NC}"
    
    # Copiar Limine para partição ESP
    mkdir -p "$esp_mount/EFI/BOOT"
    cp limine/uefi/BOOTX64.EFI "$esp_mount/EFI/BOOT/"
    
    # Copiar arquivos limine
    cp limine/bios/limine-bios.sys "$esp_mount/limine-bios.sys"
    cp limine/bios/limine-bios-hdd.bin "$esp_mount/limine-bios-hdd.bin"
    
    echo "Limine UEFI instalado em $esp_mount/EFI/BOOT/"
}

install_limine_bios() {
    local target_disk="$1"
    echo -e "${GREEN}Instalando Limine para BIOS/Legacy...${NC}"
    
    # Instalar no MBR
    dd if=limine/bios/limine-bios.sys of="$target_disk" bs=440 count=1 conv=notrunc
    
    echo "Limine BIOS instalado em $target_disk"
}

# Main
BOOT_TYPE=$(detect_boot_type)
echo -e "${YELLOW}Tipo de boot detectado: $BOOT_TYPE${NC}"

# Exemplo de uso
# install_grub_uefi "/boot"
# install_grub_bios "/dev/sda"
# install_clover_uefi "/boot/efi"
# install_clover_bios "/dev/sda"
# install_limine_uefi "/boot/efi"
# install_limine_bios "/dev/sda"
```

---

## Instalação Automática com Calamares

### hooks/install_bootloader.py

```python
#!/usr/bin/env python3
"""
Hook do Calamares para instalação automática de bootloader
Coloque em: /usr/lib/calamares/hooks/
"""

import os
import subprocess
import shutil

def get_esp_mount():
    """Retorna o ponto de montagem da partição ESP"""
    result = subprocess.run(
        ['mount'],
        capture_output=True, text=True
    )
    for line in result.stdout.split('\n'):
        if 'esp' in line.lower() or 'efi' in line.lower():
            parts = line.split()
            if len(parts) >= 3:
                return parts[2]
    return None

def detect_boot_type():
    """Detecta UEFI ou BIOS"""
    if os.path.exists('/sys/firmware/efi'):
        return "uefi"
    return "bios"

def install_bootloader(root_mountpoint, bootloader_choice):
    """Instala o bootloader baseado na escolha do usuário"""
    
    boot_type = detect_boot_type()
    esp = get_esp_mount()
    
    bootloader_dir = os.path.dirname(os.path.realpath(__file__))
    
    if bootloader_choice == "grub":
        if boot_type == "uefi":
            # Instalar GRUB UEFI
            target_dir = os.path.join(root_mountpoint, "boot")
            uefi_dir = os.path.join(target_dir, "EFI", "BOOT")
            os.makedirs(uefi_dir, exist_ok=True)
            
            # Copiar arquivos GRUB UEFI
            src_uefi = os.path.join(bootloader_dir, "grub", "uefi")
            for f in os.listdir(src_uefi):
                shutil.copy2(
                    os.path.join(src_uefi, f),
                    uefi_dir
                )
        else:
            # Instalar GRUB BIOS
            disk = input("Digite o disco (ex: /dev/sda): ")
            subprocess.run([
                "grub-install",
                "--boot-directory=/boot",
                "--target=i386-pc",
                disk
            ])
    
    elif bootloader_choice == "clover":
        if boot_type == "uefi":
            # Instalar Clover UEFI
            esp_dir = os.path.join(esp or "/boot/efi", "EFI", "BOOT")
            os.makedirs(esp_dir, exist_ok=True)
            
            shutil.copy2(
                os.path.join(bootloader_dir, "clover", "uefi", "BOOTX64.efi"),
                os.path.join(esp_dir, "BOOTX64.efi")
            )
        else:
            # Instalar Clover BIOS
            disk = input("Digite o disco (ex: /dev/sda): ")
            shutil.copy2(
                os.path.join(bootloader_dir, "clover", "bios", "boot7"),
                disk
            )

# Called by Calamares
def run():
    # Configurações (você pode obter do Calamares)
    root_mountpoint = "/tmp/calamares-root"  # Exemplo
    bootloader_choice = "grub"  # ou "clover"
    
    install_bootloader(root_mountpoint, bootloader_choice)
    return None
```

---

## Detecção de Hardware

### Verificar suporte UEFI

```python
def check_uefi_support():
    """Verifica se o hardware suporta UEFI"""
    import os
    
    checks = {
        "/sys/firmware/efi/efivars": "EFI vars",
        "/sys/firmware/efi/fw_platform_size": "EFI size",
    }
    
    supported = {}
    for path, name in checks.items():
        supported[name] = os.path.exists(path)
    
    return supported
```

### Listar opções de boot disponíveis

```python
def get_boot_options():
    """Retorna opções de bootloader disponíveis"""
    options = []
    
    if os.path.exists('/sys/firmware/efi'):
        options.append({
            "id": "uefi",
            "name": "UEFI",
            "bootloaders": ["grub-uefi", "clover-uefi"]
        })
    else:
        options.append({
            "id": "bios", 
            "name": "BIOS/Legacy",
            "bootloaders": ["grub-bios", "clover-bios"]
        })
    
    return options
```

---

## Configuração Recomendada

### Para 100% de compatibilidade:

1. **Detecte o tipo de boot** automaticamente
2. **Instale ambos** os bootloaders (GRUB + Clover)
3. **Configure fallback** (se UEFI falhar, usar BIOS)

### Estrutura de instalação:

```
ESP (partição EFI):
├── EFI/
│   ├── BOOT/
│   │   └── BOOTX64.EFI     ← Clover (primário UEFI)
│   ├── GRUB/
│   │   └── grubx64.efi     ← GRUB (fallback UEFI)
│   └── CLOVER/
│       └── CLOVERX64.efi   ← Clover config
```

### MBR (para BIOS):
- `boot7` → primeiros 440 bytes do MBR
- `boot0af` → para dual-boot macOS

---

## Troubleshooting

### BIOS não detecta bootloader
```bash
# Recriar configuração GRUB
grub-mkconfig -o /boot/grub/grub.cfg

# Reinstalar
grub-install /dev/sda
```

### UEFI não inicia
```bash
# Verificar partida EFI
efibootmgr -v

# Criar entrada EFI
efibootmgr -c -d /dev/sda -p 1 -l "\\EFI\\BOOT\\BOOTX64.EFI" -n "Clover"
```

### Secure Boot
```bash
# Para sistemas com Secure Boot, assine os binários
sbsign --key MOK.key --cert MOK.crt BOOTX64.efi --output BOOTX64.efi
```

---

## Licença

- **GRUB**: GPLv3
- **Clover**: BSD-2-Clause

## Créditos

- GRUB: https://www.gnu.org/software/grub/
- Clover: https://github.com/CloverHackyColor/CloverBootloader
