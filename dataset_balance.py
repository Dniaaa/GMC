import numpy as np
import math
import pandas as pd
from collections import Counter
from matplotlib import pyplot as plt
from scipy.ndimage import convolve1d
from utils import get_lds_kernel_window, read_txt_to_floats

def get_bin_idx(value):
    result = math.floor(value)  # round down to integer
    return result

def cal_mos_weights(labels_real, ks=5, sigma=2, plus=10):
    labels = 100 * (labels_real - labels_real.min()) / (labels_real.max() - labels_real.min())  ## normalize to [0, 100]
    bin_index_per_label = [math.floor(label) for label in labels]

    Nb = max(bin_index_per_label) + 1
    num_samples_of_bins = dict(Counter(bin_index_per_label))

    numbers = np.arange(0, Nb, 1)
    emp_label_dist = [num_samples_of_bins.get(i, 0) for i in numbers]

    # lds_kernel_window: [ks,], here for example, we use gaussian, ks=5, sigma=2
    lds_kernel_window = get_lds_kernel_window(kernel='gaussian', ks=ks, sigma=sigma)
    # calculate effective label distribution: [Nb,]
    eff_label_dist = convolve1d(np.array(emp_label_dist), weights=lds_kernel_window, mode='constant')
    eff_label_dist = eff_label_dist / eff_label_dist.sum() * sum(emp_label_dist)

    # Use re-weighting based on effective label distribution, sample-wise weights: [Ns,]
    eff_num_per_label1 = [eff_label_dist[bin_idx] for bin_idx in bin_index_per_label]
    eff_num_per_label2 = [emp_label_dist[bin_idx] for bin_idx in bin_index_per_label]

    weights = np.array([np.float32(1 / x) * plus for x in eff_num_per_label1])

    return weights

def gaussian(x, mu, sigma):
    '''
    :param x: given x-coordinate
    :param mu: mean
    :param sigma: standard deviation
    :return: probability value
    '''
    return np.exp(-(x - mu)**2 / (2 * (sigma + 1e-8)**2))

def cal_mos_weights_gaussian(labels_real, std_real, plus=100):
    
    labels = 100 * (labels_real - labels_real.min()) / (labels_real.max() - labels_real.min())
    scale_factor = 100 / (labels_real.max() - labels_real.min())
    std = std_real * scale_factor
    bin_index_per_label = [math.floor(label) for label in labels]

    Nb = math.floor(max(labels)) + 1
    numbers = np.arange(0, Nb, 1)
    eff_label_dist = []

    for x in numbers:
        score = np.sum([gaussian(x, mu, sigma) for mu, sigma in zip(labels, std)])
        eff_label_dist.append(score)
    
    eff_num_per_label = [eff_label_dist[bin_idx] for bin_idx in bin_index_per_label]
    
    weights = np.array([np.float32(1 / x) * plus for x in eff_num_per_label])
    return weights


if __name__ == '__main__':
    # 如果数据集不提供 std
    file_path = "./data/meta_info_SPAQDataset.csv"
    df = pd.read_csv(file_path)
    labels_real = df['mos'].to_numpy()
    
    weights = cal_mos_weights(labels_real)
    print(weights)

    # 如果数据集提供 std
    file_path = "./data/meta_info_LIVEChallengeDataset.csv"
    df = pd.read_csv(file_path)
    labels_real = df['mos'].to_numpy()
    std_real = df['std'].to_numpy()
    
    weights = cal_mos_weights_gaussian(labels_real, std_real)
    print(weights)
