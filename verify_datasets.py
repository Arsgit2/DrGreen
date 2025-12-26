
import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict
import json


class DatasetVerifier:
    """Проверка статуса датасетов"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.results = {}
        
    def get_dir_size(self, path: Path) -> int:
        """Получить размер директории в байтах"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except (OSError, PermissionError):
            return 0
        return total
    
    def format_size(self, size_bytes: int) -> str:
        """Форматировать размер в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
    
    def count_images(self, path: Path) -> int:
        """Подсчитать количество изображений"""
        extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        count = 0
        try:
            for file in path.rglob('*'):
                if file.is_file() and file.suffix.lower() in extensions:
                    count += 1
        except (OSError, PermissionError):
            return 0
        return count
    
    def count_classes(self, path: Path) -> int:
        """Подсчитать количество классов (папок верхнего уровня)"""
        if not path.exists():
            return 0
        try:
            classes = [d for d in path.iterdir() if d.is_dir()]
            return len(classes)
        except (OSError, PermissionError):
            return 0
    
    def get_class_distribution(self, path: Path) -> dict:
        """Получить распределение изображений по классам"""
        distribution = defaultdict(int)
        extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
        
        if not path.exists():
            return {}
        
        try:
            # Попробуем разные структуры
            # PlantVillage: class_folders с изображениями
            for class_dir in path.iterdir():
                if class_dir.is_dir():
                    count = sum(1 for f in class_dir.rglob('*')
                              if f.is_file() and f.suffix.lower() in extensions)
                    if count > 0:
                        distribution[class_dir.name] = count
        except (OSError, PermissionError):
            return {}
        
        return dict(distribution)
    
    def verify_plantvillage(self) -> dict:
        """Проверить PlantVillage датасет"""
        path = self.data_dir / "plantvillage"
        
        info = {
            "name": "PlantVillage (emmarex/plantdisease)",
            "path": str(path),
            "exists": path.exists(),
            "status": "❌ Не загружен",
            "images": 0,
            "classes": 0,
            "size": "0 B",
            "classes_detail": {}
        }
        
        if not path.exists():
            return info
        
        try:
            size = self.get_dir_size(path)
            images = self.count_images(path)
            classes = self.count_classes(path)
            distribution = self.get_class_distribution(path)
            
            info.update({
                "status": "✅ Загружен",
                "images": images,
                "classes": classes,
                "size": self.format_size(size),
                "size_bytes": size,
                "classes_detail": distribution
            })
            
        except Exception as e:
            info["status"] = f"⚠️  Ошибка: {e}"
        
        return info
    
    def verify_plantdoc(self) -> dict:
        """Проверить PlantDoc датасет"""
        path = self.data_dir / "plantdoc"
        
        info = {
            "name": "PlantDoc (pratikkayal/plantdoc-dataset)",
            "path": str(path),
            "exists": path.exists(),
            "status": "❌ Не загружен",
            "images": 0,
            "classes": 0,
            "size": "0 B",
            "splits": {},
            "classes_detail": {}
        }
        
        if not path.exists():
            return info
        
        try:
            total_images = 0
            total_classes = 0
            total_size = 0
            splits = {}
            all_classes = defaultdict(int)
            
            # PlantDoc часто имеет структуру: train/, test/, val/
            for split in ['train', 'test', 'val']:
                split_path = path / split
                if split_path.exists():
                    split_images = self.count_images(split_path)
                    split_classes = self.count_classes(split_path)
                    split_size = self.get_dir_size(split_path)
                    
                    splits[split] = {
                        "images": split_images,
                        "classes": split_classes,
                        "size": self.format_size(split_size)
                    }
                    
                    total_images += split_images
                    total_size += split_size
                    
                    # Собрать все классы
                    distribution = self.get_class_distribution(split_path)
                    for cls_name, count in distribution.items():
                        all_classes[cls_name] += count
            
            # Если нет разделов, считать как один датасет
            if not splits:
                total_images = self.count_images(path)
                total_classes = self.count_classes(path)
                total_size = self.get_dir_size(path)
                all_classes = self.get_class_distribution(path)
            else:
                total_classes = len(set(c for classes in [
                    self.get_class_distribution(path / split)
                    for split in ['train', 'test', 'val'] if (path / split).exists()
                ] for c in classes.keys()))
            
            info.update({
                "status": "✅ Загружен",
                "images": total_images,
                "classes": total_classes,
                "size": self.format_size(total_size),
                "size_bytes": total_size,
                "splits": splits,
                "classes_detail": dict(all_classes)
            })
            
        except Exception as e:
            info["status"] = f"⚠️  Ошибка: {e}"
        
        return info
    
    def verify_all(self) -> dict:
        """Проверить все датасеты"""
        self.results = {
            "plantvillage": self.verify_plantvillage(),
            "plantdoc": self.verify_plantdoc(),
            "data_dir_exists": self.data_dir.exists(),
            "data_dir": str(self.data_dir)
        }
        return self.results
    
    def print_summary(self, detailed: bool = False, stats: bool = False):
        """Вывести итоговую информацию"""
        if not self.results:
            self.verify_all()
        
        print("\n" + "="*70)
        print("📊 Статус датасетов AgroScan AI")
        print("="*70 + "\n")
        
        # PlantVillage
        pv = self.results["plantvillage"]
        status_emoji = "✅" if pv["status"] == "✅ Загружен" else "❌"
        print(f"{status_emoji} PlantVillage (emmarex/plantdisease)")
        print(f"   📁 Расположение: {pv['path']}")
        print(f"   📦 Статус: {pv['status']}")
        
        if pv["exists"]:
            print(f"   🖼️  Изображений: {pv['images']:,}")
            print(f"   🏷️  Классов: {pv['classes']}")
            print(f"   📊 Размер: {pv['size']}")
            
            if detailed and pv['classes_detail']:
                print(f"\n   📋 Классы (первые 10):")
                for i, (cls_name, count) in enumerate(sorted(
                    pv['classes_detail'].items(), 
                    key=lambda x: -x[1])[:10], 1):
                    print(f"      {i:2}. {cls_name}: {count:,} изображений")
                if len(pv['classes_detail']) > 10:
                    print(f"      ... и еще {len(pv['classes_detail']) - 10}")
        print()
        
        # PlantDoc
        pd = self.results["plantdoc"]
        status_emoji = "✅" if pd["status"] == "✅ Загружен" else "❌"
        print(f"{status_emoji} PlantDoc (pratikkayal/plantdoc-dataset)")
        print(f"   📁 Расположение: {pd['path']}")
        print(f"   📦 Статус: {pd['status']}")
        
        if pd["exists"]:
            print(f"   🖼️  Изображений: {pd['images']:,}")
            print(f"   🏷️  Классов: {pd['classes']}")
            print(f"   📊 Размер: {pd['size']}")
            
            if pd['splits']:
                print(f"\n   📂 Разделы:")
                for split_name, split_info in pd['splits'].items():
                    print(f"      {split_name}/: {split_info['images']:,} изображений, "
                          f"{split_info['classes']} классов, {split_info['size']}")
            
            if detailed and pd['classes_detail']:
                print(f"\n   📋 Классы (первые 10):")
                for i, (cls_name, count) in enumerate(sorted(
                    pd['classes_detail'].items(), 
                    key=lambda x: -x[1])[:10], 1):
                    print(f"      {i:2}. {cls_name}: {count:,} изображений")
                if len(pd['classes_detail']) > 10:
                    print(f"      ... и еще {len(pd['classes_detail']) - 10}")
        print()
        
        # Статистика
        if stats or (pv["exists"] and pd["exists"]):
            pv_size_gb = pv.get("size_bytes", 0) / (1024**3)
            pd_size_gb = pd.get("size_bytes", 0) / (1024**3)
            total_size_gb = pv_size_gb + pd_size_gb
            total_images = pv.get("images", 0) + pd.get("images", 0)
            
            print("="*70)
            print("📈 Общая статистика")
            print("="*70)
            print(f"   Всего изображений: {total_images:,}")
            print(f"   Всего классов: {pv.get('classes', 0) + pd.get('classes', 0)}")
            print(f"   Общий размер: {self.format_size(pv.get('size_bytes', 0) + pd.get('size_bytes', 0))}")
            
            if pv.get("images", 0) > 0 and pd.get("images", 0) > 0:
                print(f"\n   ✅ Оба датасета готовы к использованию!")
            elif pv.get("images", 0) > 0:
                print(f"\n   ⚠️  PlantVillage готов. PlantDoc не загружен.")
            elif pd.get("images", 0) > 0:
                print(f"\n   ⚠️  PlantDoc готов. PlantVillage не загружен.")
            else:
                print(f"\n   ❌ Датасеты не загружены. Запустите:")
                print(f"      python download_datasets.py")
        
        print("\n" + "="*70 + "\n")
    
    def save_report(self, filename: str = "datasets_report.json"):
        """Сохранить отчет в JSON"""
        if not self.results:
            self.verify_all()
        
        # Готовим данные для сохранения
        report = {
            "timestamp": str(Path.cwd()),
            "data_dir": str(self.data_dir),
            "datasets": {}
        }
        
        for name, info in self.results.items():
            if name not in ['data_dir_exists', 'data_dir']:
                info_copy = info.copy()
                # Удалить size_bytes для JSON
                info_copy.pop('size_bytes', None)
                report["datasets"][name] = info_copy
        
        report_path = Path(filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Отчет сохранен: {report_path}")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Проверка статуса датасетов AgroScan AI"
    )
    
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Показать список всех классов"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Показать подробную статистику"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Сохранить отчет в datasets_report.json"
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Папка с датасетами (по умолчанию: data)"
    )
    
    args = parser.parse_args()
    
    verifier = DatasetVerifier(args.data_dir)
    verifier.verify_all()
    verifier.print_summary(detailed=args.detailed, stats=args.stats or args.report)
    
    if args.report:
        verifier.save_report()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Прерваны пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
