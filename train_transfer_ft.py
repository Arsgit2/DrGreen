#!/usr/bin/env python3
"""
Full fine-tune training script with class balancing (oversampling) and stronger augmentations.
Saves best checkpoint to `model/plant_disease_resnet18_ft.pth`.
"""
import argparse
import time
import json
from datetime import datetime
from pathlib import Path
from collections import Counter

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, ConcatDataset, WeightedRandomSampler, Subset, Dataset
from torchvision import datasets, transforms, models

try:
    from torchvision.models import ResNet18_Weights
except Exception:
    ResNet18_Weights = None


class ReindexedConcatDataset(Dataset):
    """ConcatDataset with reindexed class labels for proper multi-dataset training."""
    def __init__(self, datasets_list, target_offsets):
        self.datasets = datasets_list
        self.target_offsets = target_offsets
        self.cumulative_sizes = torch.tensor([0] + [len(d) for d in datasets_list]).cumsum(0).tolist()
    
    def __len__(self):
        return self.cumulative_sizes[-1]
    
    def __getitem__(self, idx):
        # Find which dataset this index belongs to
        dataset_idx = 0
        for i, cum_size in enumerate(self.cumulative_sizes[:-1]):
            if idx < self.cumulative_sizes[i + 1]:
                dataset_idx = i
                break
        
        # Get the sample from the appropriate dataset
        local_idx = idx - self.cumulative_sizes[dataset_idx]
        image, label = self.datasets[dataset_idx][local_idx]
        
        # Shift label by offset
        shifted_label = label + self.target_offsets[dataset_idx]
        return image, shifted_label


def get_transforms():
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.6, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(0.3, 0.3, 0.3, 0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    return train_transform, val_transform


def load_datasets(batch_size, num_workers, device):
    train_transform, val_transform = get_transforms()

    datasets_loaded = []

    pv_path = Path('data/plantvillage')
    if pv_path.exists():
        pv_dataset = datasets.ImageFolder(str(pv_path), transform=train_transform)
        datasets_loaded.append(pv_dataset)
        print(f"   PlantVillage: {len(pv_dataset):,} images, {len(pv_dataset.classes)} classes")

    pd_train_path = Path('data/plantdoc/train')
    if pd_train_path.exists():
        pd_dataset = datasets.ImageFolder(str(pd_train_path), transform=train_transform)
        datasets_loaded.append(pd_dataset)
        print(f"   PlantDoc: {len(pd_dataset):,} images, {len(pd_dataset.classes)} classes")

    if not datasets_loaded:
        raise RuntimeError('No datasets found in data/')

    # Compute offsets for reindexing class labels
    target_offsets = []
    offset = 0
    for ds in datasets_loaded:
        target_offsets.append(offset)
        num_classes_in_ds = len(ds.classes)
        offset += num_classes_in_ds

    # Use custom dataset that reindexes labels on-the-fly
    combined = ReindexedConcatDataset(datasets_loaded, target_offsets)

    # collect targets in combined order (with reindexed labels)
    all_targets = []
    for ds_idx, ds in enumerate(datasets_loaded):
        if hasattr(ds, 'targets'):
            targets = list(ds.targets)
        elif hasattr(ds, 'samples'):
            targets = [s[1] for s in ds.samples]
        else:
            raise RuntimeError('Cannot read targets from dataset')
        
        # Shift indices by offset
        shifted_targets = [t + target_offsets[ds_idx] for t in targets]
        all_targets.extend(shifted_targets)

    total_samples = len(all_targets)
    num_classes = len(set(all_targets))

    # compute class weights inverse to frequency
    class_counts = Counter(all_targets)
    class_weights = [0.0] * num_classes
    for cls, cnt in class_counts.items():
        class_weights[cls] = total_samples / (cnt + 1e-6)

    # create deterministic split
    generator = torch.Generator()
    generator.manual_seed(42)
    perm = torch.randperm(len(combined), generator=generator).tolist()
    train_size = int(0.8 * len(combined))
    train_idx = perm[:train_size]
    val_idx = perm[train_size:]

    train_dataset = Subset(combined, train_idx)
    val_dataset = Subset(combined, val_idx)

    # ensure validation uses val_transform on underlying datasets
    for ds in datasets_loaded:
        try:
            ds.transform = val_transform
        except Exception:
            pass

    # per-sample weights for combined dataset
    sample_weights = [class_weights[t] for t in all_targets]

    sampler = WeightedRandomSampler([sample_weights[i] for i in train_idx], num_samples=len(train_idx), replacement=True)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, sampler=sampler, num_workers=num_workers, pin_memory=(device=='cuda'))
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=(device=='cuda'))

    print(f"Combined dataset: total {len(combined):,}, classes {num_classes}")

    return train_loader, val_loader, class_weights, num_classes


def build_model(arch: str, pretrained: bool, num_classes: int, fine_tune: bool):
    if arch == 'resnet18':
        if pretrained and ResNet18_Weights is not None:
            model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        else:
            try:
                model = models.resnet18(pretrained=pretrained)
            except Exception:
                model = models.resnet18()

        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
    else:
        raise ValueError('Unsupported arch: ' + arch)

    if not fine_tune:
        for name, param in model.named_parameters():
            if 'fc' not in name:
                param.requires_grad = False

    return model


def train_transfer(args):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\nDevice: {device}")
    if device == 'cuda':
        print(f" GPU: {torch.cuda.get_device_name(0)}")

    train_loader, val_loader, class_weights, num_classes = load_datasets(args.batch_size, args.num_workers, device)

    model = build_model(args.arch, args.pretrained, num_classes, fine_tune=args.fine_tune)
    model = model.to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total params: {total_params:,}, Trainable: {trainable_params:,}")

    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.AdamW(params, lr=args.lr, weight_decay=1e-4)

    try:
        weight_tensor = torch.tensor(class_weights, dtype=torch.float)
        criterion = nn.CrossEntropyLoss(weight=weight_tensor.to(device))
    except Exception:
        criterion = nn.CrossEntropyLoss()

    best_val_loss = float('inf')
    train_losses = []
    val_losses = []

    for epoch in range(args.epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        epoch_start = time.time()
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / len(train_loader)
        train_acc = 100 * correct / total if total > 0 else 0.0
        train_losses.append(train_loss)

        # validation
        model.eval()
        vloss = 0.0
        vcorrect = 0
        vtotal = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)

                vloss += loss.item()
                _, preds = torch.max(outputs, 1)
                vcorrect += (preds == labels).sum().item()
                vtotal += labels.size(0)

        val_loss = vloss / len(val_loader)
        val_acc = 100 * vcorrect / vtotal if vtotal > 0 else 0.0
        val_losses.append(val_loss)

        epoch_time = time.time() - epoch_start
        print(f"Epoch [{epoch+1}/{args.epochs}] Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}% | Time: {epoch_time:.1f}s")

        # save best
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            Path('model').mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), 'model/plant_disease_resnet18_ft.pth')
            print('  -> Best model saved to model/plant_disease_resnet18_ft.pth')

    # save training info
    info = {
        'timestamp': datetime.now().isoformat(),
        'arch': args.arch,
        'pretrained': args.pretrained,
        'fine_tune': args.fine_tune,
        'num_classes': num_classes,
        'train_losses': train_losses,
        'val_losses': val_losses,
        'epochs': args.epochs
    }
    with open('model/training_info_resnet18_ft.json', 'w') as f:
        json.dump(info, f, indent=2)
    print('Training finished. Info saved to model/training_info_resnet18_ft.json')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arch', type=str, default='resnet18')
    parser.add_argument('--pretrained', action='store_true')
    parser.add_argument('--fine-tune', dest='fine_tune', action='store_true', help='Fine-tune all layers. If not set, only head is trained.')
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--lr', type=float, default=1e-5)
    parser.add_argument('--num-workers', type=int, default=4)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    print('\n=== Transfer Learning: ResNet18 (full fine-tune w/ balancing) ===')
    print(f"Fine-tune all layers: {args.fine_tune}")

    train_transfer(args)
