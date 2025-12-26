#!/usr/bin/env python3
"""Evaluate a trained ResNet18 model on the combined PlantVillage+PlantDoc validation split.

Saves:
 - model/eval_report_resnet18.json (summary + per-class metrics)
 - model/eval_per_class.csv
 - model/eval_confusion.png

Usage:
  python eval_model.py --model-path model/plant_disease_resnet18.pth --batch-size 32
"""
import argparse
import json
from pathlib import Path
from typing import List

import torch
import torch.nn as nn
from torchvision import models, transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np
import os

from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import csv


class SimpleFilesDataset(Dataset):
    def __init__(self, paths: List[str], labels: List[int], transform=None):
        self.paths = paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        p = self.paths[idx]
        label = self.labels[idx]
        img = Image.open(p)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img, label


def collect_files_and_labels(root_paths: List[Path]):
    files = []
    labels = []
    class_names: List[str] = []
    # We'll map class name -> global index while preserving order of roots
    for root in root_paths:
        if not root.exists():
            continue
        ds = ImageFolder(str(root))
        # ensure global class_names contains dataset classes in order
        for c in ds.classes:
            if c not in class_names:
                class_names.append(c)
        # for each sample, convert local label index to class name, then to global index
        for fp, local_label in ds.samples:
            class_name = ds.classes[local_label]
            global_label = class_names.index(class_name)
            files.append(fp)
            labels.append(global_label)
    return files, labels, class_names


def build_model(num_classes, model_path: str):
    model = models.resnet18(weights=None)
    in_f = model.fc.in_features
    model.fc = nn.Linear(in_f, num_classes)
    if Path(model_path).exists():
        sd = torch.load(model_path, map_location='cpu')
        
        # Filter out fc layer weights if they don't match
        fc_weight_shape = sd.get('fc.weight', None)
        if fc_weight_shape is not None:
            expected_shape = torch.Size([num_classes, in_f])
            if fc_weight_shape.shape != expected_shape:
                print(f"  Skipping fc layer (shape mismatch: {fc_weight_shape.shape} vs {expected_shape})")
                del sd['fc.weight']
                if 'fc.bias' in sd:
                    del sd['fc.bias']
        
        model.load_state_dict(sd, strict=False)
        print(f"Loaded weights from {model_path}")
    else:
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return model


def evaluate(model, dataloader, device):
    model.to(device)
    model.eval()
    y_true = []
    y_pred = []
    y_prob = []
    soft = nn.Softmax(dim=1)
    with torch.no_grad():
        for imgs, labels in dataloader:
            imgs = imgs.to(device)
            outputs = model(imgs)
            probs = soft(outputs).cpu().numpy()
            preds = np.argmax(probs, axis=1)
            y_true.extend(labels.numpy().tolist())
            y_pred.extend(preds.tolist())
            y_prob.extend(probs.tolist())
    return np.array(y_true), np.array(y_pred), np.array(y_prob)


def save_confusion(conf_mat, class_names, out_path):
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(conf_mat, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(conf_mat.shape[1]), yticks=np.arange(conf_mat.shape[0]),
           xticklabels=class_names, yticklabels=class_names,
           xlabel='Predicted label', ylabel='True label', title='Confusion matrix')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    fmt = 'd'
    thresh = conf_mat.max() / 2.
    for i in range(conf_mat.shape[0]):
        for j in range(conf_mat.shape[1]):
            ax.text(j, i, format(conf_mat[i, j], fmt), ha='center', va='center',
                    color='white' if conf_mat[i, j] > thresh else 'black')
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', type=str, default='model/plant_disease_resnet18.pth')
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--num-workers', type=int, default=4)
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    args = parser.parse_args()

    # Collect files
    roots = [Path('data/plantvillage'), Path('data/plantdoc/train')]
    files, labels, class_names = collect_files_and_labels(roots)
    if not files:
        raise RuntimeError('No images found in data/plantvillage or data/plantdoc/train')

    # Deterministic split 80/20
    from sklearn.model_selection import train_test_split
    train_files, val_files, train_labels, val_labels = train_test_split(
        files, labels, test_size=0.20, stratify=labels, random_state=42
    )

    # transforms
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_dataset = SimpleFilesDataset(val_files, val_labels, transform=val_transform)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

    num_classes = len(set(labels))
    model = build_model(num_classes=num_classes, model_path=args.model_path)

    y_true, y_pred, y_prob = evaluate(model, val_loader, args.device)

    # metrics
    labels_range = list(range(len(class_names)))
    report = classification_report(y_true, y_pred, labels=labels_range, target_names=class_names, output_dict=True, zero_division=0)
    conf_mat = confusion_matrix(y_true, y_pred, labels=labels_range)

    Path('model').mkdir(parents=True, exist_ok=True)
    
    # Determine output suffix based on model path
    model_name = Path(args.model_path).stem  # e.g., 'plant_disease_resnet18_ft' or 'plant_disease_resnet18'
    if '_ft' in model_name:
        suffix = '_ft'
    else:
        suffix = ''
    
    # save report
    report_path = f'model/eval_report_resnet18{suffix}.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # save per-class csv
    csv_path = f'model/eval_per_class{suffix}.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.writer(cf)
        writer.writerow(['class', 'precision', 'recall', 'f1-score', 'support'])
        for cls in class_names:
            row = report.get(cls, {})
            writer.writerow([cls, row.get('precision', 0), row.get('recall', 0), row.get('f1-score', 0), row.get('support', 0)])

    # save confusion matrix image
    confusion_path = f'model/eval_confusion{suffix}.png'
    save_confusion(conf_mat, class_names, confusion_path)

    print(f'Evaluation finished. Reports saved under model/ ({suffix if suffix else "baseline"})')


if __name__ == '__main__':
    main()
