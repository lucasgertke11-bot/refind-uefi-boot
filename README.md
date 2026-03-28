# rEFInd UEFI Bootloader

rEFInd é um gerenciador de boot UEFI moderno e visualmente atraente.

## Suporte

| Recurso | Suportado |
|---------|-----------|
| UEFI | ✅ Sim |
| BIOS | ❌ Não |
| Secure Boot | ✅ Sim (com keys) |

## Arquiteturas

- **x86_64** (refind_x64.efi) - PCs modernos
- **IA32** (refind_ia32.efi) - PCs antigos 32-bit
- **AA64** (refind_aa64.efi) - ARM64

## Estrutura de Arquivos

```
/boot/efi/EFI/refind/
├── refind_x64.efi        # Bootloader principal 64-bit
├── refind_ia32.efi       # Bootloader 32-bit
├── refind_aa64.efi       # Bootloader ARM64
├── refind.conf-sample    # Configuração de exemplo
├── drivers_x64/          # Drivers para 64-bit
├── drivers_ia32/         # Drivers para 32-bit
├── drivers_aa64/         # Drivers para ARM64
├── icons/                # Ícones do menu
├── keys/                 # Chaves Secure Boot
└── tools_x64/           # Ferramentas
```

## Instalação

### Método 1: Manual

1. Copie os arquivos para a partição EFI:
```bash
mkdir -p /boot/efi/EFI/refind
cp -r refind_x64.efi drivers_x64 icons keys /boot/efi/EFI/refind/
```

2. Configure o EFI:
```bash
efibootmgr --create --disk /dev/sda --part 1 --label "rEFInd" --loader "\\EFI\\refind\\refind_x64.efi"
```

### Método 2: refind-install

```bash
./refind-install
```

## Configuração

Edite `refind.conf` para personalizar:

- Timeout do menu
- Tema e ícones
- Entradas de boot
- Parâmetros do kernel

## Distribuições Suportadas

- Ubuntu ✅
- Debian ✅
- Fedora ✅
- Arch Linux ✅
- Gentoo ✅

## Instalação por Distribuição

### Ubuntu/Debian
```bash
# EFI está em /boot/efi
sudo cp -r boot/efi/EFI/refind /boot/efi/EFI/
```

### Fedora
```bash
# EFI está em /boot/efi
sudo cp -r boot/efi/EFI/refind /boot/efi/EFI/
```

### Arch Linux
```bash
# EFI está em /boot
sudo cp -r boot/efi/EFI/refind /boot/EFI/
```

### Gentoo
```bash
# EFI está em /boot/efi
sudo cp -r boot/efi/EFI/refind /boot/efi/EFI/
```

## Limitações

- Não suporta BIOS/Legacy boot
- Requer UEFI para funcionar
- Instalação mais complexa que GRUB

---

**Versão**: 0.14.2  
**Licença**: GPLv3  
**Website**: http://www.rodsbooks.com/refind/
