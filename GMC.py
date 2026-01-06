import numpy as np
import pandas as pd
from utils import read_txt_to_floats

def GMC(Q, Qd, pred, label, std, weights, plus, method):
    '''
    :param Q: quality
    :param Qd: quality range
    :param pred: predicted quality from model
    :param label: MOS
    :param std: standard deviation of MOS per image
    :param weights: selection probability per image
    :param method: method to compute correlation coefficient
    :param plus: multiplier to scale std
    :return: computed correlation coefficient
    '''
    # Check if inputs are column vectors, if not, make them column vectors

    if pred.ndim == 1:
        pred = pred[:, np.newaxis]
    if label.ndim == 1:
        label = label[:, np.newaxis]
    if std.ndim == 1:
        std = std[:, np.newaxis]
    if weights.ndim == 1:
        weights = weights[:, np.newaxis]

    # Re-rank scores
    label_r = np.unique(label, return_inverse = True)[1]
    pred_r = np.unique(pred, return_inverse = True)[1]
    label_r = label_r[:, np.newaxis]
    pred_r = pred_r[:, np.newaxis]

    len_data = len(label_r)

    total = 0
    Ps = []
    for i in range(len_data - 1):
        wi = weights[:len_data - i - 1] * weights[i + 1:]  # remove dataset bias
        Ps.append(wi)
        total += np.sum(wi)

    omega = 0
    w_list = []
    if method == 'KRCC':
        # Pre-computing for importance weight w
        for i in range(len_data - 1):
            diff = np.abs(label[:len_data - i - 1] - label[i + 1:])   # use absolute value because we compute quality range
            sigma = (std[:len_data - i - 1] * plus)**2 + (std[i + 1:] * plus)**2
            PQi = np.exp(-(Q - label[:len_data - i - 1]) ** 2 / (2 * (std[:len_data - i - 1] * plus)** 2))
            PQj = np.exp(-(Q - label[i + 1:]) ** 2 / (2 * (std[i + 1:] * plus) ** 2))
            PQd = np.exp(-(Qd - diff)**2 / (2 * sigma))
            wi = PQi * PQj * PQd * Ps[i]
            w_list.append(wi)
            omega += np.sum(wi)
        for i in range(len_data - 1):
            w_list[i] = w_list[i] / omega

    er_rate = 0
    aij_total = 0
    bij_total = 0
    sum = 0
    for i in range(len_data - 1):
        if method == 'KRCC':
            temp_pred = pred[:len_data - i - 1] - pred[i + 1:]        # compute KRCC
            temp_label = label[:len_data - i - 1] - label[i + 1:]
            er_label = np.sign(temp_pred) * np.sign(temp_label)
            er_rate += np.sum(w_list[i] * er_label)
        else:
            temp_pred = None
            temp_label = None
            if method == 'PLCC':
                temp_pred = pred[:len_data - i - 1] - pred[i + 1:]        # compute PLCC
                temp_label = label[:len_data - i - 1] - label[i + 1:]
            if method == 'SRCC':
                temp_pred = pred_r[:len_data - i - 1] - pred_r[i + 1:]     # compute SRCC using ranks
                temp_label = label_r[:len_data - i - 1] - label_r[i + 1:]

            er_label = temp_pred * temp_label
            diff = np.abs(label[:len_data - i - 1] - label[i + 1:])
            sigma = (std[:len_data - i - 1] * plus) ** 2 + (std[i + 1:] * plus) ** 2
            PQi = np.exp(-(Q - label[:len_data - i - 1]) ** 2 / (2 * (std[:len_data - i - 1] * plus)** 2))
            PQj = np.exp(-(Q - label[i + 1:]) ** 2 / (2 * (std[i + 1:] * plus) ** 2))
            PQd = np.exp(-(Qd - diff) ** 2 / (2 * sigma))

            wi = PQi * PQj * PQd * Ps[i]    # applicable to PLCC and SRCC
            er_rate += np.sum(wi * er_label)
            aij_total += np.sum(wi * (temp_label ** 2))
            bij_total += np.sum(wi * (temp_pred ** 2))

    if method == 'KRCC':
        return er_rate    # applicable to KRCC
    else:
        w2 = 1.0 / (np.sqrt(aij_total) * np.sqrt(bij_total))
        score = er_rate * w2
        return score   # applicable to PLCC, SRCC

if __name__ == '__main__':
    plus = 1
    metric_list = ['qualiclip', 'qualiclip+']
    # metric_list = ['qualiclip', 'qualiclip+']  #'clipiqa', 'clipiqa+', 'niqe','qalign', 'topiq_nr'
    # 'ssim', 'psnr','ms_ssim','DeepWSD','lpips','dists'

    # std per image
    # path1 = "./data/meta_info_LIVEChallengeDataset.csv"
    # df = pd.read_csv(path1)
    # std = df['std'].to_numpy()

    ## std of all images
    path3 = "./results/SPAQ/mos_std.txt"
    std = read_txt_to_floats(path3)
    std = np.array(std)

    ## weights of all images
    # weight file
    path4 = "./results/SPAQ/weight/weights_rough.txt"
    weights = read_txt_to_floats(path4)
    weights = np.array(weights)

    sample_num = 100

    # sampled file
    file_path = f'./results/SPAQ/sampled_data/sample{sample_num}.xlsx'
    data = pd.read_excel(file_path)
    samples = data[['Q', 'Qd']].values.tolist()

    for metric in metric_list:
        path2 = "./data/SPAQ/{}.csv".format(metric)
        data = pd.read_csv(path2)
        pred = data['Results Scores for CC'].to_numpy()
        label = data['Ground Truth Labels'].to_numpy()
        methods = ['PLCC','SRCC','KRCC']  #'PLCC','SRCC',
        for method in methods:
            X = []
            Y = []
            rate_list = []
            w2_list = []
            scores = []
            for Q, Qd in samples:
                score = GMC(Q, Qd, pred, label, std, weights, plus, method)
                scores.append(score)
                print(Q, Qd, score)
                X.append(Q)
                Y.append(Qd)
            data = pd.DataFrame({'质量': X, '质量差异': Y, method: scores})
            data.to_excel(f'./results/实验三_rough/SPAQ/{metric}/{method}.xlsx', index=False)

    # val_PLCC = round(stats.pearsonr(pred, label)[0], 4)
    # print("PLCC:",val_PLCC)
    #
    # val_SROCC = round(stats.spearmanr(pred, label)[0], 4)
    # print("SRCC:",val_SROCC)
    #
    # val_KROCC = round(stats.stats.kendalltau(pred, label)[0], 4)
    # print("KRCC:",val_KROCC )

