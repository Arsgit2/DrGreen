#!/usr/bin/env python3
"""Запуск улучшенного обучения модели"""
import subprocess
import sys

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 ЗАПУСК УЛУЧШЕННОГО ОБУЧЕНИЯ МОДЕЛИ")
    print("=" * 80)
    print("\nПараметры обучения:")
    print("  - Pretrained веса ImageNet: ДА")
    print("  - Fine-tune всех слоев: ДА")
    print("  - Эпох: 50")
    print("  - Batch size: 32")
    print("  - Learning rate: 1e-4")
    print("\nЭто может занять некоторое время...")
    print("=" * 80)
    
    # Запускаем обучение
    cmd = [
        sys.executable,
        "train_improved.py",
        "--pretrained",
        "--fine-tune",
        "--epochs", "50",
        "--batch-size", "32",
        "--lr", "1e-4",
        "--weight-decay", "1e-4",
        "--early-stop-patience", "10"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n⚠️ Обучение прервано пользователем")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n\n❌ Ошибка при обучении: {e}")
        sys.exit(1)



