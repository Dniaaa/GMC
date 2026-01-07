<div align="center">

<h1>From Global to Granular: Revealing IQA Model Performance via Correlation Surface</h1>

<div>
    <a href='https://scholar.google.com/citations?hl=zh-CN&user=w_WL27oAAAAJ' target='_blank'>Baoliang Chen</a><sup>1,2</sup>&emsp;
    <a href='' target='_blank'>Danni Huang</a><sup>1</sup>&emsp;
    <a href='https://dblp.org/pid/214/8898.html' target='_blank'>Hanwei Zhu</a><sup>2</sup>&emsp;
    <a href='https://github.com/lingyzhu0101' target='_blank'>Lingyu Zhu</a><sup>3</sup>&emsp;
    <a href='' target='_blank'>Shiqi Wang</a><sup>3</sup>&emsp;
    <a href='' target='_blank'>Weisi Lin</a><sup>2</sup>
</div>
<div>
    <sup>1</sup>South China Normal University, China&emsp; 
    <sup>2</sup>Nanyang Technological University, Singapore&emsp; 
    <sup>3</sup>City University of Hong Kong, China&emsp; 
</div>

<div>
    <h4 align="center">
        • <a href="https://github.com/Baoliang93/GMC" target='_blank'>[Code]</a> • 
        <a href="https://htmlpreview.github.io/?https://github.com/Baoliang93/GMC/blob/main/test/ssim_kadid10k.html" target='_blank'>[Try Interactive Demo]</a> •
    </h4>
</div>

<img src="assets/flow.png" width="1000px"/>

<br>

<strong>The proposed Granularity-Modulated Correlation (GMC) measure reveals IQA model behavior through a structured correlation surface, providing a more informative and reliable paradigm for analyzing, comparing, and deploying IQA models.</strong>

---

## :bar_chart: Correlation Surface Visualization

<div align="left">

<table>
  <tr>
    <td width="55%">
        <strong>Interactive Performance Diagnosis:</strong><br>
        The GMC framework generates structured 3D surfaces that visualize IQA model consistency. Unlike traditional metrics that provide a single global score, our correlation surface reveals how model reliability fluctuates across different <b>Quality Scales</b> and <b>Quality Differences</b>. 
        <br><br>
    </td>
    <td width="45%" align="center">
        <a href="https://htmlpreview.github.io/?https://github.com/Baoliang93/GMC/blob/main/test/ssim_kadid10k.html">
            <img src="assets/example4.gif" alt="GMC Interactive Demo" width="100%">
        </a>
    </td>
  </tr>
</table>

</div>

> **Tip:** Click the link in the header or the interactive animation above to open the **full interactive 3D surface** in your browser.
---

</div>

## :hammer_and_wrench: Installation

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/Baoliang93/GMC.git
cd GMC

# Install dependencies
pip install numpy pandas scipy statsmodels plotly openpyxl
```

---

## :rocket: Quick Start

Generate your own 3D correlation surface with a single command:

### Basic Usage
The tool automatically detects MOS and prediction columns. If standard deviation (STD) is not provided, it will be estimated automatically.

```bash
python main.py --pred-file ./data/SPAQ/qualiclip.csv
```

### Advanced Usage (Specify Columns & Output)
```bash
python main.py --pred-file ./test/pred_ssim_kadid10k.csv \
               --weights-file ./results/kadid10k_Gauss/weights.txt \
               --sample-file ./results/kadid10k_Gauss/sample100.xlsx \
               --output ./test/ssim_kadid10k.html
```

### Key Parameters
- `--pred-file`: Path to input data (CSV/XLSX).
- `--pred-cols`: Comma-separated list of prediction columns.
- `--mos-col`: Name of the MOS column (default: `mos`).
- `--method`: Correlation type: `SRCC`, `PLCC`, or `KRCC`.
- `--samples`: Number of Latin Hypercube samples (default: `100`).
- `--output`: Path to save the interactive HTML plot.

---

## :file_folder: Repository Structure

- `GMC.py`: Core logic for Granularity-Modulated Correlation calculation.
- `main.py`: Main entry point for the CLI tool.
- `multi_surface.py`: Surface fitting and 3D visualization using Plotly.
- `sampling.py`: Latin Hypercube Sampling (LHS) for efficient performance estimation.
- `dataset_balance.py`: Weight calculation and distribution modulation.
- `std_deviation.py`: Automated MOS standard deviation estimation.

---

## :love_you_gesture: Citation

If you find this work useful for your research, please consider citing our paper:

```bibtex
@article{chen2024granular,
  title={From Global to Granular: Revealing IQA Model Performance via Correlation Surface},
  author={Chen, Baoliang and Huang, Danni and Zhu, Hanwei and Zhu, Lingyu and Wang, Shiqi and Lin, Weisi},
  journal={Submitted to IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)},
  year={2024}
}
```

## :envelope: Contact

For any questions, please feel free to reach out to:
- **Baoliang Chen**: [blchen6-c@my.cityu.edu.hk](mailto:blchen6-c@my.cityu.edu.hk)
- **Danni Huang**: [dannyhuang@m.scnu.edu.cn](mailto:dannyhuang@m.scnu.edu.cn)
