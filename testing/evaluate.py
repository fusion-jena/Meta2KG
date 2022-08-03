from os.path import join
import pandas as pd
from sklearn.metrics import classification_report
from config import gt_path, solved_path

if __name__ == '__main__':

    repos = ['idiv', 'gbif', 'pangaea', 'dryad', 'dataworld', 'bexis', 'befchina']

    all_gt, all_pred = [], []
    for repo in repos:
        # load gt
        gt_file = join(gt_path, '{}_gt.csv'.format(repo))
        df_gt = pd.read_csv(gt_file, header=0)
        gt = df_gt['gt'].tolist()
        gt_keys = df_gt['Metadata Key'].tolist()
        all_gt.extend(gt)

        # load predictions
        pred_file = join(solved_path, '{}_solutions.csv'.format(repo))
        df_pred = pd.read_csv(pred_file, header=0)
        pred = df_pred['Prediction'].tolist()
        pred_keys = df_pred['Metadata Key'].tolist()
        all_pred.extend(pred)

        for i, g in enumerate(gt):
            if not g:
                print(i)

        print('{}:\n'.format(repo))
        # print classification report per repo
        print(classification_report(gt, pred, labels=list(set(gt)), zero_division=0))
        # break
        print('=========================')
    # print classification report for all repos (all repos are equal weight)
    print('Classification Report for all repos:\n')
    print(classification_report(all_gt, all_pred, labels=list(set(all_gt)), zero_division=1))
