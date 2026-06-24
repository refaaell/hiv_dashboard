from flask import Flask, render_template, jsonify
import pandas as pd
import json

app = Flask(__name__)

# Load data once
df = pd.read_csv('dinkes-od_18510_jumlah_kasus_hiv_berdasarkan_kabupatenkota_v3_data.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    years = sorted(df['tahun'].unique().tolist())
    kabupaten = sorted(df['nama_kabupaten_kota'].unique().tolist())
    records = df.to_dict(orient='records')
    
    # Summary per year
    yearly_summary = []
    for y in years:
        ydf = df[df['tahun'] == y]
        yearly_summary.append({
            'tahun': int(y),
            'total': int(ydf['jumlah_kasus'].sum()),
            'rata_rata': round(float(ydf['jumlah_kasus'].mean()), 1),
            'tertinggi': {
                'kab': ydf.loc[ydf['jumlah_kasus'].idxmax(), 'nama_kabupaten_kota'],
                'kasus': int(ydf['jumlah_kasus'].max())
            },
            'terendah': {
                'kab': ydf.loc[ydf['jumlah_kasus'].idxmin(), 'nama_kabupaten_kota'],
                'kasus': int(ydf['jumlah_kasus'].min())
            }
        })
    
    # Trend per kabupaten
    trend = {}
    for kab in kabupaten:
        kdf = df[df['nama_kabupaten_kota'] == kab].sort_values('tahun')
        trend[kab] = {
            'tahun': kdf['tahun'].tolist(),
            'kasus': kdf['jumlah_kasus'].tolist()
        }
    
    return jsonify({
        'years': years,
        'kabupaten': kabupaten,
        'records': records,
        'yearly_summary': yearly_summary,
        'trend': trend
    })

@app.route('/api/map/<int:year>')
def get_map_data(year):
    ydf = df[df['tahun'] == year][['kode_kabupaten_kota', 'nama_kabupaten_kota', 'jumlah_kasus']]
    result = {}
    for _, row in ydf.iterrows():
        result[int(row['kode_kabupaten_kota'])] = {
            'nama': row['nama_kabupaten_kota'],
            'kasus': int(row['jumlah_kasus'])
        }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
