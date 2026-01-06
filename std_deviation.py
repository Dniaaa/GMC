import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import norm

# simple unimodal Beta distribution
def estimate_std_from_mos(mos, phi=8):
    """
    Estimate standard deviation based on Beta distribution
    :param mos: input MOS value (scalar or array)
    :param phi: precision parameter (tune; larger -> smaller std)
    :param score_range: original score range, e.g., (1, 5)
    :return: estimated standard deviation
    """
    # map MOS to [0, 1] interval

    low = min(mos)
    high = max(mos)
    mu_beta = (mos - low) / (high - low)

    var_beta = (mu_beta * (1 - mu_beta)) / (phi + 1)

    std = np.sqrt(var_beta) * (high - low)
    return std

if __name__ == '__main__':
    path1 = "./data/meta_info_PIPALDataset.csv"
    df = pd.read_csv(path1)
    label = df['mos'].to_numpy()

    std_estimated = estimate_std_from_mos(label,phi=3)
    output_path = "./results/pipal/mos_std.txt"  # custom save path
    np.savetxt(output_path, std_estimated, fmt="%.4f", delimiter="\n")

