from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import os
import shutil

app = Flask(__name__)

# Ensure static folder for outputs exists
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_gmc():
    data = request.json
    
    # Root directory of GMC
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    cmd = ['python', 'main.py']
    
    if data.get('pred_file'):
        cmd.extend(['--pred-file', data['pred_file']])
    if data.get('mos_col'):
        cmd.extend(['--mos-col', data['mos_col']])
    if data.get('pred_cols'):
        cmd.extend(['--pred-cols', data['pred_cols']])
    if data.get('std_col'):
        cmd.extend(['--std-col', data['std_col']])
    if data.get('method'):
        cmd.extend(['--method', data['method']])
    if data.get('samples'):
        cmd.extend(['--samples', str(data['samples'])])
        
    # Output file path relative to output dir
    output_filename = "plot.html"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    cmd.extend(['--output', output_path])
    
    try:
        # Run GMC process
        process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        
        output_str = out.decode('utf-8', errors='ignore')
        error_str = err.decode('utf-8', errors='ignore')
        
        if process.returncode == 0 and os.path.exists(output_path):
            return jsonify({
                'status': 'success', 
                'output': output_str,
                'plot_url': f'/static/outputs/{output_filename}?t={os.path.getmtime(output_path)}'
            })
        else:
            return jsonify({
                'status': 'error', 
                'error': error_str or "Output plot.html was not created. Please check inputs."
            })
            
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

if __name__ == '__main__':
    print("Starting GMC Web GUI on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
