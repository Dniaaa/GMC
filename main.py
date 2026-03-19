import argparse
import os
import numpy as np
import pandas as pd
from GMC import GMC
from sampling import LHS
from dataset_balance import cal_mos_weights, cal_mos_weights_gaussian
from multi_surface import cal_Score
import plotly.graph_objects as go
from utils import read_txt_to_floats
from std_deviation import estimate_std_from_mos

def load_table(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    return pd.read_csv(path)

def autodetect_columns(df, mos_col, pred_cols, std_col):
    cols = list(df.columns)
    mos_candidates = [mos_col, "mos", "Ground Truth Labels"]
    std_candidates = [std_col, "std"]
    mos = None
    for c in mos_candidates:
        if c and c in cols:
            mos = c
            break
    if mos is None:
        num_cols = [c for c in cols if np.issubdtype(df[c].dtype, np.number)]
        if len(num_cols) == 0:
            raise ValueError("No numeric columns found for MOS.")
        mos = num_cols[0]
    std = None
    for c in std_candidates:
        if c and c in cols:
            std = c
            break
    if pred_cols:
        preds = [c for c in pred_cols.split(",") if c in cols]
        if len(preds) == 0:
            raise ValueError("None of the specified pred columns found.")
    else:
        numeric = [c for c in cols if np.issubdtype(df[c].dtype, np.number)]
        exclude = set([mos] + ([std] if std else []))
        preds = [c for c in numeric if c not in exclude]
        if len(preds) == 0:
            raise ValueError("No prediction columns detected.")
    return mos, std, preds

def compute_weights(labels, std, use_gaussian, ks, sigma, weight_plus):
    if use_gaussian and std is not None:
        return cal_mos_weights_gaussian(labels, std, plus=weight_plus)
    return cal_mos_weights(labels, ks=ks, sigma=sigma, plus=weight_plus)

def build_surfaces(pred_dict, labels, std, weights, samples, plus, method, bound, bw_method, grid_res):
    x = []
    y = []
    z_list = []
    for name, pred in pred_dict.items():
        scores = []
        n = len(samples)
        prefix = f"Computing GMC for {name}:"
        for idx, (Q, Qd) in enumerate(samples):
            score = GMC(Q, Qd, pred, labels, std, weights, plus, method)
            scores.append(score)
            pct = int((idx + 1) * 100 / n)
            bar_len = 30
            filled = int(bar_len * (idx + 1) / n)
            bar = "█" * filled + "-" * (bar_len - filled)
            print(f"\r{prefix} Progress {pct:3d}% [{bar}]", end="", flush=True)
        print()
        x = [s[0] for s in samples]
        y = [s[1] for s in samples]
        z_list.append(np.array(scores))
    avg_heights, xi_grid, yi_grid, zi_list = cal_Score(np.array(x), np.array(y), z_list, bound=bound, bw_method=bw_method, grid_res=grid_res)
    return avg_heights, xi_grid, yi_grid, zi_list

def plot_surfaces(xi_grid, yi_grid, zi_list, model_names, output_html):
    colorscales = ["Viridis", "Plasma", "Rainbow", "Hot", "Portland", "peach", "emrld", "turbo", "Spectral", "Thermal"]
    mos_min = float(np.nanmin(xi_grid))
    mos_max = float(np.nanmax(xi_grid))
    x_tickvals = np.round(np.linspace(mos_min, mos_max, 5)).astype(int).tolist()
    y_tickvals = np.round(np.linspace(0, mos_max - mos_min, 5)).astype(int).tolist()

    fig = go.Figure()
    for i, (name, zi) in enumerate(zip(model_names, zi_list)):
        fig.add_trace(go.Surface(x=xi_grid, y=yi_grid, z=zi, name=name, opacity=0.8, showscale=False, colorscale=colorscales[i % len(colorscales)], cmin=float(np.nanmin(zi)), cmax=float(np.nanmax(zi))))
    fig.update_layout(width=900, height=900, template="plotly", font=dict(family="Times New Roman", size=16, color="black"), scene=dict(xaxis=dict(title=dict(text="Quality Scale", font=dict(size=24)), tickvals=x_tickvals), yaxis=dict(title=dict(text="Quality Difference", font=dict(size=24)), tickvals=y_tickvals), zaxis=dict(title=dict(text="GMC Score", font=dict(size=24)), tickvals=[0.2,0.3,0.4,0.5,0.6]), camera=dict(eye=dict(x=0.9, y=-2.55, z=0.375))))
    fig.update_traces(showlegend=True)
    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    fig.write_html(output_html, include_plotlyjs="cdn")
    return output_html

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred-file", type=str, required=True)
    parser.add_argument("--pred-cols", type=str, default="")
    parser.add_argument("--mos-col", type=str, default="mos")
    parser.add_argument("--std-col", type=str, default="")
    parser.add_argument("--std-file", type=str, default="")
    parser.add_argument("--weights-file", type=str, default="")
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--method", type=str, default="SRCC", choices=["PLCC","SRCC","KRCC"])
    parser.add_argument("--std-scale", type=float, default=1.0)
    parser.add_argument("--weight-plus", type=float, default=10.0)
    parser.add_argument("--ks", type=int, default=5)
    parser.add_argument("--sigma", type=float, default=2.0)
    parser.add_argument("--bw-method", type=str, default="cv_ls")
    parser.add_argument("--grid-res", type=int, default=100)
    parser.add_argument("--output", type=str, default="results/3d/plot.html")
    parser.add_argument("--sample-file", type=str, default="")
    args = parser.parse_args()

    df = load_table(args.pred_file)
    mos_col, std_col, pred_cols = autodetect_columns(df, args.mos_col, args.pred_cols, args.std_col)
    labels = df[mos_col].to_numpy()
    std = None
    if args.std_file:
        std = np.array(read_txt_to_floats(args.std_file))
    elif std_col:
        std = df[std_col].to_numpy()
    else:
        std = estimate_std_from_mos(labels)
    if args.weights_file:
        weights = np.array(read_txt_to_floats(args.weights_file))
    else:
        use_gaussian = std is not None and np.all(np.isfinite(std))
        weights = compute_weights(labels, std if use_gaussian else None, use_gaussian, args.ks, args.sigma, args.weight_plus)
    lower_bound = float(labels.min())
    upper_bound = float(labels.max())
    if args.sample_file:
        sdf = load_table(args.sample_file)
        if ("Q" in sdf.columns) and ("Qd" in sdf.columns):
            samples = sdf[["Q", "Qd"]].to_numpy()
        else:
            raise ValueError("Sample file must contain columns 'Q' and 'Qd'.")
    else:
        samples = LHS(samples=args.samples, bound=(lower_bound, upper_bound))
    pred_dict = {c: df[c].to_numpy() for c in pred_cols}
    avg_heights, xi_grid, yi_grid, zi_list = build_surfaces(pred_dict, labels, std, weights, samples, args.std_scale, args.method, bound=(lower_bound, upper_bound), bw_method=args.bw_method, grid_res=args.grid_res)
    for i, name in enumerate(pred_dict.keys()):
        print(f"{name}'s GMC({args.method}) is {avg_heights[i]}")
    print("Rendering figure...")
    plot_path = plot_surfaces(xi_grid, yi_grid, zi_list, list(pred_dict.keys()), args.output)
    print(f"Figure saved to {plot_path}. Open in a browser to view.")

if __name__ == "__main__":
    main()
