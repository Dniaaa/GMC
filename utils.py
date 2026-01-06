import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal.windows import triang

def get_lds_kernel_window(kernel, ks, sigma):
    assert kernel in ['gaussian', 'triang', 'laplace']
    half_ks = (ks - 1) // 2
    if kernel == 'gaussian':
        base_kernel = [0.] * half_ks + [1.] + [0.] * half_ks
        kernel_window = gaussian_filter1d(base_kernel, sigma=sigma) / max(gaussian_filter1d(base_kernel, sigma=sigma))
    elif kernel == 'triang':
        kernel_window = triang(ks)
    else:
        laplace = lambda x: np.exp(-abs(x) / sigma) / (2. * sigma)
        kernel_window = list(map(laplace, np.arange(-half_ks, half_ks + 1))) / max(
            map(laplace, np.arange(-half_ks, half_ks + 1)))

    return kernel_window

def read_txt_to_floats(file_path):
    float_list = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                float_list.append(float(line.strip()))
            except ValueError:
                print(f"Cannot convert to float: {line.strip()}")
    return float_list
