#!/usr/bin/env python3
import json

bl = json.load(open('model/eval_report_resnet18.json'))
ft = json.load(open('model/eval_report_resnet18_ft.json'))

print('=' * 60)
print('СРАВНЕНИЕ: Baseline vs Fine-tune')
print('=' * 60)

acc_bl = bl.get('accuracy', 0)
acc_ft = ft.get('accuracy', 0)
f1_bl = bl.get('macro avg', {}).get('f1-score', 0)
f1_ft = ft.get('macro avg', {}).get('f1-score', 0)

print(f'\nAccuracy:')
print(f'  Baseline:  {acc_bl:.4f}')
print(f'  Fine-tune: {acc_ft:.4f}')
print(f'  Δ {acc_ft - acc_bl:+.4f} ({(acc_ft - acc_bl) / acc_bl * 100:+.1f}%')

print(f'\nMacro F1:')
print(f'  Baseline:  {f1_bl:.4f}')
print(f'  Fine-tune: {f1_ft:.4f}')
print(f'  Δ {f1_ft - f1_bl:+.4f} ({(f1_ft - f1_bl) / f1_bl * 100:+.1f}%')

print(f'\nТОП 5 классов (Fine-tune):\n')
top_ft = sorted([(k, v['f1-score']) for k, v in ft.items() if isinstance(v, dict)], key=lambda x: -x[1])[:5]
for i, (cls, score) in enumerate(top_ft, 1):
    print(f'  {i}. {cls}: {score:.3f}')

print(f'\nАртефакты:')
print(f'  - model/plant_disease_resnet18_ft.pth (best checkpoint)')
print(f'  - model/eval_report_resnet18_ft.json')
print(f'  - model/eval_per_class_ft.csv')
print(f'  - model/eval_confusion_ft.png')
