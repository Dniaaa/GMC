import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.nonparametric.kernel_regression import KernelReg
import plotly.graph_objects as go

def cal_Score(x, y, z_list, bound, bw_method='cv_ls', grid_res=100):
    """
    Fit surfaces for multiple models and return average height
    :param x: original data x coordinates
    :param y: original data y coordinates
    :param z_list: list of z data for multiple models
    :param bound: specified range [x_min, x_max]
    :param bw_method: bandwidth selection method for kernel regression ('cv_ls', 'aic', or custom)
    :param grid_res: grid resolution
    :return: average height value for each model
    """
    x, y = np.asarray(x), np.asarray(y)
    delta = bound[1] - bound[0]
    # generate prediction grid
    xi = np.linspace(bound[0], bound[1], grid_res)
    yi = np.linspace(0, delta, grid_res)
    xi_grid, yi_grid = np.meshgrid(xi, yi)
    grid_points = np.column_stack((xi_grid.ravel(), yi_grid.ravel()))

    avg_heights = []
    zi_list = []  # store surfaces for all models
    for z in z_list:
        z = np.asarray(z)
        exog = np.column_stack((x, y))
        kr = KernelReg(endog=z, exog=exog, var_type='cc', reg_type='ll', bw=bw_method)

        Z, _ = kr.fit(grid_points)
        Z = Z.reshape(xi_grid.shape)
        Z = np.nan_to_num(Z)  # handle NaN

        # compute average height
        dx = xi[1] - xi[0]
        dy = yi[1] - yi[0]
        volume = np.trapz(np.trapz(Z, axis=0, dx=dx), dx=dy)
        area = (bound[1] - bound[0]) * delta
        avg_height = np.round(volume / area, 4) if area != 0 else 0

        avg_heights.append(avg_height)
        zi_list.append(Z)

    return avg_heights, xi_grid, yi_grid, zi_list


def plot_interactive_surfaces(xi_grid, yi_grid, zi_list, model_names):
    """
    Generate interactive 3D surface plots
    :param xi_grid: x-coordinate grid
    :param yi_grid: y-coordinate grid
    :param zi_list: list of z values for all models
    :param model_names: list of model names
    """
    import plotly.io as pio
    print(pio.templates.keys())
    # color schemes (Plotly built-in)
    colorscales = [
        'Viridis',     # blue-green gradient (tech style)
        'Plasma',      # purple-red gradient (high contrast)
        'Rainbow',     # full spectrum gradient (clear separation)
        'Hot',         # black-red-yellow gradient (warm palette)
        'Portland',    # pink-orange-blue gradient (cool palette)

        'peach',  # blue-purple
        'emrld',  # pink-purple-blue-cyan-yellow
        'turbo',  # blue-cyan-yellow-red
        'Spectral',  # pink-yellow
        'Thermal'
    ]
    fig = go.Figure()
    # 为每个模型添加曲面
    for i, (name, zi) in enumerate(zip(model_names, zi_list)):
        fig.add_trace(
            go.Surface(
                x=xi_grid,
                y=yi_grid,
                z=zi,
                name=name,
                opacity=0.8,  # set transparency to distinguish overlapping surfaces
                showscale=False,  # avoid multiple color bars overlapping
                # cycle colorscales
                colorscale = colorscales[i % len(colorscales)],
                # optional color range adjustment (example)
                cmin = np.nanmin(zi),
                cmax = np.nanmax(zi)
            )
        )
    # 配置布局
    fig.update_layout(
        width=900,  # set figure width to 900 px
        height=900,  # set figure height to 900 px
        template="plotly",    ## "ggplot2"
        # title=f'Interactive Model Surfaces - {dataset}',
        font=dict(
            family='Times New Roman',
            size=20,
            color='black'
        ),
        scene=dict(
            xaxis=dict(
                title=dict(
                    text='',
                    font=dict(
                        size=36
                    ),
                ),
                # specify tick label locations
                tickvals=[1,2,3,4,5],
                # tickvals=[0, 0.5, 1],

                # tickmode='linear',
                # nticks=3,
            ),
            yaxis=dict(
                title=dict(
                    text='',
                    font=dict(
                        size=36
                    ),
                ),
                # specify tick label locations
                tickvals=[0,1,2,3,4],

                # tickmode='linear',
                # nticks=5,
            ),
            zaxis=dict(
                title=dict(
                    text='',
                    font = dict(
                        color='white'
                    )
                ),
                tickvals=[0.2,0.3,0.4,0.5,0.6], # specify tick label locations as needed
            ),
            camera=dict(
                eye=dict(x=0.6*1.5, y=-1.7*1.5, z=0.25*1.5),  # view angle
            ),
        ),
        legend=dict(
            x=0.9,
            y=0.8,
            xanchor='left',
            yanchor='top',
            font=dict(size=30),  # change legend font size
        ),
        hovermode='x unified',
        # updatemenus=[dict(
        #     type="buttons",
        #     buttons=[dict(label="Show All",
        #                   method="update",
        #                   args=[{"visible": [True] * len(zi_list)}])]
        # )]
    )
    ## adjust label standoff distances from axes
    fig.update_xaxes(title_standoff=40)
    fig.update_yaxes(title_standoff=60)

    fig.update_scenes(xaxis_ticklen=5)
    fig.update_scenes(yaxis_ticklen=5)
    fig.update_scenes(zaxis_ticklen=25)

    # fig.update_scenes(zaxis_tick0=20)

    fig.update_scenes(xaxis_tickangle= 0)
    fig.update_scenes(yaxis_tickangle=0)
    fig.update_scenes(zaxis_tickangle=-10)

    # by default, allow hiding surfaces by clicking legend
    fig.update_traces(showlegend=True)
    # fig.show()
    fig.write_image(f"images/example.png", scale=8)


if __name__ == '__main__':
    cc = 'SRCC'   ## modify as needed
    path2 = "data/meta_info_KADID10kDataset.csv"
    df = pd.read_csv(path2)
    label = df['mos'].to_numpy()
    lower_bound = min(label)  # minimum value
    upper_bound = max(label)  # maximum value

    metric_list = ['ssim']
    ##'ssim','psnr','ms_ssim','DeepWSD','lpips', 'dists'
    ## ,'qualiclip', 'qualiclip+'
    #'ssim','psnr','ms_ssim','lpips', 'dists'
    #'clipiqa', 'clipiqa+', 'niqe','qalign', 'topiq_nr','qualiclip','qualiclip+'

    z_list = []
    file_path = 'results/kadid10k_Gauss/{}/{}.xlsx'.format(metric_list[0], cc)  # replace with your file path
    data = pd.read_excel(file_path)
    x = np.array(data['质量'])
    y = np.array(data['质量差异'])

    for metric in metric_list:
        file_path = 'results/kadid10k_Gauss/{}/{}.xlsx'.format(metric, cc)  # replace with your file path
        data = pd.read_excel(file_path)
        z = np.array(data[cc])
        z_list.append(z)

    ## begin: plot 3D surfaces + compute averages
    avg_heights, xi_grid, yi_grid, zi_list = cal_Score(x, y, z_list, bound=(lower_bound, upper_bound))
    plot_interactive_surfaces(xi_grid, yi_grid, zi_list, metric_list)   ## plot interactive 3D surfaces

    # output average height for each model
    for i, label in enumerate(metric_list):
        print(f"{label}'s {cc} = {avg_heights[i]}")

