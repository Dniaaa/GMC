import numpy as np
import pandas as pd

def LHS(samples, bound):
    '''
    Generate 2D Latin Hypercube sampling points, where:
    - First dimension: range [bound[0], bound[1]]
    - Second dimension: range [0, bound[1]-bound[0]]
    :param samples: number of samples
    :param bound: value range for the first dimension, format [min, max]
    :return: sampling array of shape (samples, 2)
    '''
    dim = 2  # fixed to 2D
    result = np.zeros((samples, dim))
    delta = bound[1] - bound[0]  # max value of second dimension
    # process first dimension (original data range)
    intervals_dim1 = np.linspace(bound[0], bound[1], samples + 1)
    points_dim1 = np.random.uniform(intervals_dim1[:-1], intervals_dim1[1:])
    np.random.shuffle(points_dim1)
    result[:, 0] = points_dim1
    # process second dimension (difference range 0 ~ delta)
    intervals_dim2 = np.linspace(0, delta, samples + 1)
    points_dim2 = np.random.uniform(intervals_dim2[:-1], intervals_dim2[1:])
    np.random.shuffle(points_dim2)
    result[:, 1] = points_dim2
    return result

if __name__ == '__main__':
    ## MOS of all images
    path1 = "./data/meta_info_KADID10kDataset.csv"
    df = pd.read_csv(path1)
    labels = df['mos'].to_numpy()  ## MOS per image

    sample_num = [100]
    for n_samples in sample_num:
        output_file_path = f'./results/采样一致性验证/kadid10k/随机采样/sampled_data1/sample{n_samples}.xlsx'

        dim = 2  # number of dimensions
        lower_bound = min(labels)  # minimum value
        upper_bound = max(labels)  # maximum value
        print("min: {}".format(lower_bound))
        print("max: {}".format(upper_bound))

        # generate Latin hypercube samples
        samples = LHS(samples=n_samples, bound=(lower_bound, upper_bound))
        data = pd.DataFrame(samples, columns=['Q', 'Qd'])

        data.to_excel(output_file_path, index=False, engine='openpyxl')
        print(f"数据已成功保存到 {output_file_path}")


