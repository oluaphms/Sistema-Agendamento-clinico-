#!/usr/bin/env python3
"""
Script para instalar dependências necessárias para geração de relatórios PDF
"""

import subprocess
import sys
import os

def install_package(package):
    """Instala um pacote usando pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao instalar {package}")
        return False

def main():
    print("🚀 Instalando dependências para geração de relatórios PDF...")
    print("=" * 60)
    
    # Lista de pacotes necessários
    packages = [
        "reportlab==4.0.4",
        "Pillow==10.1.0"  # reportlab depende do Pillow
    ]
    
    success_count = 0
    total_packages = len(packages)
    
    for package in packages:
        print(f"\n📦 Instalando {package}...")
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resumo da instalação:")
    print(f"   ✅ Sucessos: {success_count}")
    print(f"   ❌ Falhas: {total_packages - success_count}")
    print(f"   📦 Total: {total_packages}")
    
    if success_count == total_packages:
        print("\n🎉 Todas as dependências foram instaladas com sucesso!")
        print("   O sistema agora pode gerar relatórios em PDF.")
    else:
        print("\n⚠️  Algumas dependências não puderam ser instaladas.")
        print("   O sistema usará CSV como fallback para relatórios.")
    
    print("\n💡 Dica: Se houver problemas, tente:")
    print("   1. Ativar o ambiente virtual: source venv/bin/activate (Linux/Mac)")
    print("   2. Ativar o ambiente virtual: venv\\Scripts\\activate (Windows)")
    print("   3. Executar: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
