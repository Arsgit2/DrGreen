import torch
sd = torch.load('model/plant_disease_resnet18_ft.pth', map_location='cpu')
print(f'Keys: {list(sd.keys())[:5]}')
fc_weight = sd.get('fc.weight')
if fc_weight is not None:
    print(f'FC weight shape: {fc_weight.shape}')
    print(f'FC weight stats: min={fc_weight.min():.6f}, max={fc_weight.max():.6f}, mean={fc_weight.mean():.6f}')
    print(f'Non-zero elements: {(fc_weight != 0).sum()} / {fc_weight.numel()}')
else:
    print('FC weight not found!')
