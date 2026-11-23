"""Night lights over southeast Louisiana before and after Hurricane Ida (2021).

This is an illustration for the README case study only: the models do not use images.
It downloads two single-night NASA Black Marble images (VNP46A1, VIIRS Day/Night Band
at-sensor radiance, Suomi NPP) from the NASA GIBS WMS service, which needs no account, and puts
them side by side in figures/ida_night_lights.png. We use single nights rather than the
gap-filled VNP46A2 layer, because gap filling replaces cloudy pixels with earlier nights and
hides the outage. The default dates are the clearest nights before and after landfall.

Run from the repository root (needs internet access):

    python scripts/ida_night_lights.py

NASA imagery is free to use (NASA Earth science data use policy). Credit: NASA Black Marble
VNP46A1 (DOI 10.5067/VIIRS/VNP46A1.002), served by NASA GIBS / Worldview.
"""
import argparse
import io
import urllib.parse
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

LAYER = 'VIIRS_SNPP_DayNightBand_At_Sensor_Radiance'
WMS = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi'
# lat_min, lon_min, lat_max, lon_max (WMS 1.3.0 order for EPSG:4326): New Orleans and Baton Rouge
BBOX = (29.0, -92.0, 31.0, -88.8)
CITIES = {'New Orleans': (-90.07, 29.95), 'Baton Rouge': (-91.15, 30.45), 'Houma': (-90.72, 29.60)}


def night_light(date, width=1000):
    lat0, lon0, lat1, lon1 = BBOX
    height = round(width * (lat1 - lat0) / (lon1 - lon0))
    query = {'SERVICE': 'WMS', 'REQUEST': 'GetMap', 'VERSION': '1.3.0', 'LAYERS': LAYER, 'STYLES': '',
             'CRS': 'EPSG:4326', 'BBOX': ','.join(map(str, BBOX)), 'WIDTH': width, 'HEIGHT': height,
             'FORMAT': 'image/png', 'TIME': date}
    with urllib.request.urlopen(f'{WMS}?{urllib.parse.urlencode(query)}', timeout=60) as r:
        return Image.open(io.BytesIO(r.read())).convert('RGB')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--before', default='2021-08-23', help='night before landfall (YYYY-MM-DD)')
    parser.add_argument('--after', default='2021-09-03', help='night after landfall (YYYY-MM-DD)')
    parser.add_argument('--out', default='figures/ida_night_lights.png')
    args = parser.parse_args()

    lat0, lon0, lat1, lon1 = BBOX
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), facecolor='black')
    for ax, date, label in zip(axes, [args.before, args.after], ['Before landfall', 'After landfall']):
        ax.imshow(night_light(date), extent=(lon0, lon1, lat0, lat1))
        for name, (x, y) in CITIES.items():
            ax.annotate(name, (x, y), xytext=(6, 6), textcoords='offset points', color='white', fontsize=8)
            ax.plot(x, y, 'o', ms=3, mfc='none', mec='white', mew=0.8)
        ax.set_title(f'{label} ({date})', color='white', fontsize=10)
        ax.axis('off')
    fig.text(0.5, 0.02, 'NASA Black Marble VNP46A1 (VIIRS Day/Night Band, single nights) via NASA GIBS. Ida made '
             'landfall on 29 August 2021. The grey background before is moonlight (full moon on 22 August).',
             color='#bbbbbb', ha='center', fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    Path(args.out).parent.mkdir(exist_ok=True)
    fig.savefig(args.out, dpi=150, facecolor='black', bbox_inches='tight')
    print('saved', args.out)


if __name__ == '__main__':
    main()
