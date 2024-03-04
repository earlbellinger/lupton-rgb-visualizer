#### Streamlit app for showing Lupton RGB images 

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import make_lupton_rgb
from astropy.utils.data import get_pkg_data_filename
from astropy.wcs import WCS

def load_fits(fpath, ext=0):
    with fits.open(fpath) as hdu:
        header = hdu[ext].header
        data = hdu[ext].data
    return header, np.array(data,dtype=float)

def implot(image, figsize=(8, 8), cmap='gray_r', scale=0.5, colorbar=False, header=None, wcs=None, **kwargs):
    # Setup WCS if provided through header, override if wcs directly given
    wcs = WCS(header) if header and not wcs else wcs
    subplot_kw = {'projection': wcs} if wcs else {}
    
    # Create plot with WCS projection if applicable
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=subplot_kw)
    if wcs is not None:
        ax.set_xlabel('Right Ascension [hms]', fontsize=15)
        ax.set_ylabel('Declination [degrees]', fontsize=15)
    
    # Calculate default vmin and vmax based on image statistics
    kwargs.setdefault('vmin', np.mean(image) - scale * np.std(image))
    kwargs.setdefault('vmax', np.mean(image) + scale * np.std(image))
    kwargs.setdefault('cmap', cmap)
    kwargs.setdefault('origin', 'lower')
    
    im = ax.imshow(image, **kwargs)
    if colorbar:
        plt.colorbar(im, ax=ax)
    
    ax.tick_params(direction='in', length=9, width=1.5, labelsize=15)
    
    return fig, ax

@st.cache_data
def download_data():
    g_name = get_pkg_data_filename('visualization/reprojected_sdss_g.fits.bz2')
    r_name = get_pkg_data_filename('visualization/reprojected_sdss_r.fits.bz2')
    i_name = get_pkg_data_filename('visualization/reprojected_sdss_i.fits.bz2')
    header, g = load_fits(g_name) 
    header, r = load_fits(r_name) 
    header, i = load_fits(i_name) 
    wcs = WCS(header)
    
    return g, r, i, wcs

st.title('Lupton RGB Visualizer')

stretch  = st.sidebar.slider('Stretch', min_value=0.01, max_value=2.,  value=0.5,  step=0.01)
Q        = st.sidebar.slider('Q',       min_value=0., max_value=15., value=10.0, step=0.1)
minimum  = st.sidebar.slider('minimum', min_value=0., max_value=0.2, value=0.1, step=0.01)

g, r, i, wcs = download_data() 

rgb = make_lupton_rgb(i, r, g, Q=Q, stretch=stretch, minimum=minimum)
fig, ax = implot(rgb, wcs=wcs)
ax.coords[0].set_ticks_visible(False)
ax.coords[0].set_ticklabel_visible(False)
ax.coords[1].set_ticks_visible(False)
ax.coords[1].set_ticklabel_visible(False)

st.pyplot(fig)
