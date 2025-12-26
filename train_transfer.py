
import argparse
import time
import json
from datetime import datetime
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, ConcatDataset
from torchvision import datasets, transforms, models

# Reuse dataset loading logic from train_model if available
try:
    from train_model import ModelTrainer
except Exception:
    ModelTrainer = None


def build_model(arch: str, pretrained: bool, num_classes: int, fine_tune: bool):
    if arch == 'resnet18':
        model = models.resnet18(pretrained=pretrained)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
    else:
        raise ValueError('Unsupported arch: ' + arch)

    if not fine_tune:
        # Freeze all params except classifier
        for name, param in model.named_parameters():
            if 'fc' not in name:
                param.requires_grad = False

    return model


def get_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(0.2, 0.2, 0.2),
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
    all_classes = set()

    pv_path = Path('data/plantvillage')
    if pv_path.exists():
        pv_dataset = datasets.ImageFolder(str(pv_path), transform=train_transform)
        datasets_loaded.append(pv_dataset)
        all_classes.update(pv_dataset.classes)
        print(f"   PlantVillage: {len(pv_dataset):,} images, {len(pv_dataset.classes)} classes")

    pd_train_path = Path('data/plantdoc/train')
    if pd_train_path.exists():
        pd_dataset = datasets.ImageFolder(str(pd_train_path), transform=train_transform)
        datasets_loaded.append(pd_dataset)
        all_classes.update(pd_dataset.classes)
        print(f"   PlantDoc: {len(pd_dataset):,} images, {len(pd_dataset.classes)} classes")

    if not datasets_loaded:
        raise RuntimeError('No datasets found in data/')

    combined = ConcatDataset(datasets_loaded)
    train_size = int(0.8 * len(combined))
    val_size = len(combined) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(combined, [train_size, val_size])

    # replace transforms on validation dataset
    val_dataset.dataset.transform = val_transform

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=(device=='cuda'))
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=(device=='cuda'))

    print(f"Combined dataset: total {len(combined):,}, classes {len(all_classes)}")

    return train_loader, val_loader, len(all_classes)


def train_transfer(args):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\nDevice: {device}")
    if device == 'cuda':
        print(f" GPU: {torch.cuda.get_device_name(0)}")

    # load datasets
    train_loader, val_loader, num_classes = load_datasets(args.batch_size, args.num_workers, device)

    # build model
    model = build_model(args.arch, args.pretrained, num_classes, fine_tune=args.fine_tune)
    model = model.to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total params: {total_params:,}, Trainable: {trainable_params:,}")

    # optimizer: only params that require grad
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.AdamW(params, lr=args.lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    scaler = torch.amp.GradScaler("cuda") if device == 'cuda' else None

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
            if scaler is not None:
                with torch.amp.autocast(device_type="cuda"):
                    outputs = model(images)
                    loss = criterion(outputs, labels)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

            running_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / len(train_loader)
        train_acc = 100 * correct / total
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
                if scaler is not None:
                    with torch.amp.autocast(device_type="cuda"):
                        outputs = model(images)
                        loss = criterion(outputs, labels)
                else:
                    outputs = model(images)
                    loss = criterion(outputs, labels)

                vloss += loss.item()
                _, preds = torch.max(outputs, 1)
                vcorrect += (preds == labels).sum().item()
                vtotal += labels.size(0)

        val_loss = vloss / len(val_loader)
        val_acc = 100 * vcorrect / vtotal
        val_losses.append(val_loss)

        epoch_time = time.time() - epoch_start
        print(f"Epoch [{epoch+1}/{args.epochs}] Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}% | Time: {epoch_time:.1f}s")

        # save best
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            Path('model').mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), 'model/plant_disease_resnet18.pth')
            print('  -> Best model saved to model/plant_disease_resnet18.pth')

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
    with open('model/training_info_resnet18.json', 'w') as f:
        json.dump(info, f, indent=2)
    print('Training finished. Info saved to model/training_info_resnet18.json')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--arch', type=str, default='resnet18')
    parser.add_argument('--pretrained', action='store_true')
    parser.add_argument('--fine-tune', dest='fine_tune', action='store_true', help='Fine-tune all layers. If not set, only head is trained.')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--num-workers', type=int, default=4)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    print('\n=== Transfer Learning: ResNet18 ===')
    print(f"Head-only training: {not args.fine_tune}")

    train_transfer(args)
