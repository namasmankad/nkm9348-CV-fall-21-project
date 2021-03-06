import glob as glob
import albumentations
import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import os

from model import Net

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Net().to(device)
checkpoint = torch.load('../outputs/model.pth')
model.load_state_dict(checkpoint['model_state_dict'])
root_dir = '../inputs/GTSRB/Test/Images/'

test_df = pd.read_csv(
    '../inputs/GTSRB/Test/GTSRB_Final_Test_GT/GT-final_test.csv',
    delimiter=';', nrows=10
    )
gt_df = test_df.set_index('Filename', drop=True)

sign_df = pd.read_csv(
        '../inputs/GTSRB/Training/signnames.csv'
        )

aug = albumentations.Compose([
                albumentations.Resize(48, 48, always_apply=True),
            ])


for i in range(len(test_df)):
    image_path = root_dir+test_df.loc[i, 'Filename']
    image = plt.imread(image_path)
    orig = image.copy()

    model.eval()
    with torch.no_grad():
        image = image / 255.
        image = aug(image=np.array(image))['image']
        image = np.transpose(image, (2, 0, 1))
        image = torch.tensor(image, dtype=torch.float).to(device)
        image = image.unsqueeze(0)
        outputs = model(image)
        _, preds = torch.max(outputs.data, 1)
         

    label = sign_df.loc[int(preds), 'SignName']

    filename = image_path.split('/')[-1]
    gt_id = gt_df.loc[filename].ClassId
    gt_label = sign_df.loc[int(gt_id), 'SignName']

    plt.imshow(orig)
    plt.title(f"Prediction - {str(label)}\nGround Truth - {str(gt_label)}")
    plt.axis('off')
    plt.savefig(f"../outputs/{filename.split('.')[0]}.png")
    plt.show()
    plt.close()
