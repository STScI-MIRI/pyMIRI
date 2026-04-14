#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 10:51:37 2024

@author: sshenoy
"""

"""
This is the main MakeFlat class to generate MIRI imager flats.
"""

import os
import sys

import configparser
import pandas as pd
import numpy as np
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
import matplotlib.pyplot as plt

from jwst import datamodels
from jwst.pipeline import Detector1Pipeline

import warnings

class MakeFlat(object):
    """Class to generate MIRI imager flat"""
    
    def __init__(self):
        self.inpath = None
        self.outpath = os.getcwd()
        self.manifest = None
        self.filelist = None
        self.df = None
        self.hdul = None
        self.mode = None
        self.band = None
        self.mask_outside = []
        self.sigma = None
        self.edge = 8
        self.rate_outpath = None
        
        
    def read_manifest(self, manifest, inpath='./'):
        """ Read the input manifest and generate a list of files
        to process."""
        
        # Check the input path
        if os.path.isdir(inpath):
            if inpath[-1] != '/':
                inpath = inpath + '/'
            self.inpath = inpath
        else:
            return("inpath, {}, does not exisit ".format(inpath))
        
        if os.path.isfile(self.inpath+manifest):
            self.manifest = self.inpath+manifest
        else:
            return("Input manifest, {}, does not exist".format(manifest))
        
        flist = []
        
        with open(self.manifest, 'r') as f:
            for line in f.readlines():
                if line[0] != '#':
                    flist.append(os.path.abspath(line.split()[0]))
        
        self.filelist = flist
        
        return self.filelist
    
    def make_dataframe(self, filelist):
        """Read the filelist and genarate a data frame with the 
        filenames and all the relevent metadata."""
        
        meta_data = {'FILEPATH': [],
                     'FILENAME': [],
                     'INSTRUMENT': [],
                     'EXP_TYPE': [],
                     'FILTER': [],
                     'LAMP': [],
                     'SUBARRAY': []
                     }
        
        for file in filelist:
            hdr = fits.getheader(file)
            meta_data['FILEPATH'].append(os.path.abspath(file))
            meta_data['FILENAME'].append(hdr['FILENAME'])
            meta_data['INSTRUMENT'].append(hdr['INSTRUME'])
            meta_data['EXP_TYPE'].append(hdr['EXP_TYPE'])
            meta_data['FILTER'].append(hdr['FILTER'])
            meta_data['LAMP'].append(hdr['LAMP'])
            meta_data['SUBARRAY'].append(hdr['SUBARRAY'])
        
        input_df = pd.DataFrame(meta_data)
        
        self.df = input_df
        
        return self.df
        
    def is_miri_band(self, band, mode='imager'):
        """
            Funtion to check if the give band is a part of MIRI
            filter suite

        Parameters
        ----------
        band : str
            Name of the filter/band.
        mode : str, optional
            The MIRI observing mode that uses filters (i.e. excluding all
            spectroscopy filters/disperser). Valid vaules are:
            imager, corona & tso. The default is 'imager'.

        Returns
        -------
        Boolean. Returns True if the band is a part of MIRI observing mode
        else returns False. Also returns False if the mode is not a valid
        MIRI observing mode.

        """
        
        if band is None:
            print("None is not a valid MIRI filter/band. Returning False.")
            return False
        else:
            u_band = band.upper()
            
        if mode is None:
            print("None is not a valid MIRI mode Returning False.")
            return False
        else:
            u_mode = mode.lower()
        
        self.band = u_band
        self.mode = u_mode
        
        valid_modes = ['imager', 'corona', 'tso']
        
        if u_mode not in valid_modes:
            print(" The requested mode is not a valib MIRI observing " +
                  " mode. Returing False.")
            return False
        
        if u_mode == 'imager' or u_mode == 'tso':
            valid_bands = ['F560W', 'F770W', 'F1000W', 'F1130W', 'F1280W', 
                           'F1500W', 'F1800W', 'F2100W', 'F2550W']
            if u_band in valid_bands:
                yes_no = True
            else:
                yes_no = False
        elif u_mode == 'corona':
            valid_bands = ['F1065C', 'F1140C', 'F1550C', 'F2300C']
            if u_band in valid_bands:
                yes_no = True
            else:
                yes_no = False
            
        return yes_no
    
    def filter_dataframe(self, input_df, band=None):
        
        if band is None:
            msg = " FILTER/band is undefined. Will look in the data "
            msg = msg + "header for FILTER value."
            print(msg)
            if not 'FILTER' in input_df.columns:
                print(" FILTER column is not found in the input " +
                      " dataframe. Exiting ......")
                sys.exit(1)
            else:
                barr = np.unique(input_df['FILTER'])
                print(" Found {} filter/s in the input data.".format(barr))
                if len(barr) > 1:
                    print(" Multiple filter values found in the input data. " +
                  " Processing only {}".format(barr[0]) +
                  " filter.")
            
            band = barr[0]
        
        if self.is_miri_band(band):
            self.band = band
        else:
            err_msg = "Filter, {}, is not a part of MIRI ".format(band)
            err_msg = err_msg + "imager filter suite."
            print(err_msg)
            return input_df
        
        tmp_df = input_df.copy()
        
        tmp_df = tmp_df.drop(tmp_df[tmp_df['INSTRUMENT']!='MIRI'].index)
        tmp_df = tmp_df.drop(tmp_df[tmp_df['EXP_TYPE']!='MIR_IMAGE'].index)
        tmp_df = tmp_df.drop(tmp_df[tmp_df['LAMP']!='OFF'].index)
        tmp_df = tmp_df.drop(tmp_df[tmp_df['SUBARRAY']!='FULL'].index)
        tmp_df = tmp_df.drop(tmp_df[tmp_df['FILTER']!=band].index)
        
        self.df = tmp_df.copy()
        
        return self.df
    
    def write_log_cfg(self, logfile, outdir=None):
        
        if outdir is None:
            if isinstance(self.outpath, str):
                outpath = self.outpath
            elif self.inpath is None:
                outpath = os.getcwd + 'proc/'
            else:
                outpath = self.inpath + 'proc/'
        else:
            outpath = outdir
        
        log_file = os.path.join(outpath, logfile)
        
        cfgfile = log_file.replace('.log', '.cfg')
        
        config = configparser.ConfigParser()
        config.add_section("*")
        config.set("*", "handler", "file:" + log_file)
        config.set("*", "level", "INFO")
        
        config.write(open(cfgfile, "w"))
        
        return cfgfile
    
    def read_config_file(self, cfg_file):
        """Read the confiuration file to set all the required 
        input variables."""
        
        print("Will read the cfg file later")
        params = {}
        
        return params
    
    
    def run_detector1_pipe(self, input_df, flat_file=None, 
                           asdffile=None, outdir=None):
        
        if flat_file is None:
            msg = " Using default flat file for jwst detector1 pipeline."
            print(msg)
        
        if outdir is None:
            if self.inpath is None:
                outpath = os.getcwd + 'proc/'
            else:
                outpath = self.inpath + 'proc/'
        else:
            outpath = outdir
        
        if outpath[-1] != '/':
            outpath = outpath + '/'
            
        self.outpath = outpath
            
        op_dir = outpath + 'det1out'
        if not os.path.isdir(op_dir):
            os.makedirs(op_dir)
            
        if op_dir[-1] != '/':
            op_dir = op_dir + '/'
        
        self.rate_outpath = op_dir
        
        rate_files = []
        
        for file in input_df['FILEPATH']:
            b_name = os.path.basename(file)
            r_name = b_name.replace('uncal.fits', 'rate.fits')
            
            if not os.path.isfile(op_dir + r_name):
                log_file = os.path.basename(file).replace('_uncal.fits', 
                                                          '_rate.log')
                
                cfgfile = self.write_log_cfg(log_file, outdir=op_dir)
                
                if asdffile is not None:
                    result = Detector1Pipeline.call(file, 
                                                    output_dir=op_dir, 
                                                    save_results=True,
                                                    logcfg=cfgfile,
                                                    config_file=asdffile
                                                    )
                    print(f" Using {asdffile} file in Detector1Pipeline.")
                else:
                    result = Detector1Pipeline.call(file, 
                                                    output_dir=op_dir, 
                                                    save_results=True,
                                                    logcfg=cfgfile
                                                    )
                    print(" Using default, CDRS, file in Detector1Pipeline.")
                
                if os.path.isfile(op_dir + r_name):
                    print(' Generted rate file, {}.'.format(r_name))
                    rate_files.append(r_name)
                else:
                    print('strun error for file: {}'.format(r_name))
                    rate_files.append(np.nan)   
            else:
                print(' Rate file, {}, exists.'.format(r_name))
                rate_files.append(r_name)
        
        
        input_df['RATEFILE'] = rate_files
        
        unproc_df = input_df[input_df['RATEFILE']==np.nan].copy()
        proc_df = input_df.drop(input_df[input_df['RATEFILE']==np.nan].index)
        
        unproc_df.to_csv(os.path.join(self.rate_outpath, "unproc_files.csv"),
                         index=False)
        
        self.df = proc_df
        
        return self.df
    
    
    def get_mask(self, m_file, msk_out=None, edge=None, save=False):
        
        if not os.path.isfile(m_file):
            print("\n User has not set the mask file.")
            print(" Looking for flat file in CRDS_PATH")
            c_path = os.environ.get(('CRDS_PATH'))
            if c_path is None:
                print(" CRDS_PATH is not set. Exiting ....")
                return None
            else:
                if c_path[-1] != '/': c_path = c_path + '/'
                m_file = c_path + \
                        'references/jwst/miri/jwst_miri_flat_0655.fits'
                if not os.path.isfile(m_file):
                    f_name = os.path.basename(m_file)
                    msg = " Flat File, {}, not found in CRD_PATH."
                    print(msg.format(f_name))
                    print(" WARNING: Not using flat mask.")
                    return None
        
        f_name = os.path.basename(m_file)
        print("\n Mask File: {}".format(f_name))
        hdul = fits.open(m_file)
        
        sci_arr = hdul['sci'].data.copy()
        #err_arr = hdul['err'].data.copy()
        dq_arr =hdul['dq'].data.copy()
        
        ### Mask n edge pixels.
        if edge is None:
            self.edge = 8
        else:
            self.edge = edge
            
        n = self.edge
        print(" Masking {} edge pixels.".format(n))
        
        hdul["SCI"].data[0:n, :] = np.nan
        hdul["DQ"].data[0:n, :] = 67
        hdul["ERR"].data[0:n, :] = np.inf

        hdul["SCI"].data[:, 0:n] = np.nan
        hdul["DQ"].data[:, 0:n] = 67
        hdul["ERR"].data[:, 0:n] = np.inf

        hdul["SCI"].data[-n:-1, :] = np.nan
        hdul["DQ"].data[-n:-1, :] = 67
        hdul["ERR"].data[-n:-1, :] = np.inf

        hdul["SCI"].data[:, -n:-1] = np.nan
        hdul["DQ"].data[:, -n:-1] = 67
        hdul["ERR"].data[:, -n:-1] = np.inf
        
        ### Mask low pixel values.
        
        if (msk_out is None): 
            self.mask_outside = [np.nanmin(hdul['sci'].data),
                                 np.nanmax(hdul['sci'].data)]
        else:
            self.mask_outside = msk_out
            
        
        lo_val = np.min(self.mask_outside)
        lo_mask = hdul['sci'].data < lo_val
        hdul["SCI"].data[lo_mask] = np.nan
        hdul["DQ"].data[lo_mask] = 67
        hdul["ERR"].data[lo_mask] = np.inf
        
        lo_pix = np.count_nonzero(lo_mask)
        msg = " # pix masked below pixel value of {:.2f}: {} ({:.2}%)"
        print(msg.format(lo_val, lo_pix, 100*lo_pix/(1032*1024)))
        
        ### Mask high pixel values
        hi_val = np.max(self.mask_outside)
        
        hi_mask = hdul['sci'].data > hi_val
        hdul["SCI"].data[hi_mask] = np.nan
        hdul["DQ"].data[hi_mask] = 67
        hdul["ERR"].data[hi_mask] = np.inf
        
        hi_pix = np.count_nonzero(hi_mask)
        msg = " # pix masked above pixel value of {:.2f}: {} ({:.2f}%)"
        print(msg.format(hi_val, hi_pix, 100*hi_pix/(1032*1024)))
        
        flat_mask = hdul['DQ'].data != 0 | np.isnan(hdul['sci'].data)
        
        ### Unmask the LRS slit region.
        flat_mask[294:308, 301:351] =  0
        
        nan_total = np.count_nonzero(flat_mask)
        nan_str = " Total # of pix masked: {} ({:.2f}%)\n"
        print(nan_str.format(nan_total, 100*nan_total/(1032*1024)))
        
        ### Display mask and its histogram.
        odata = np.ma.array(sci_arr, mask=(dq_arr != 0), 
                            fill_value=np.nan)
        od_min = np.nanmin(odata)
        od_max = np.nanmax(odata)
        od_mean, od_median, od_std = sigma_clipped_stats(odata)
        od_cnts, od_begs = np.histogram(odata.data,
                                       bins='fd',
                                       range=(od_min, od_max) )
        od_bmid = (od_begs[:-1] + od_begs[1:])/2
        
        
        hdata = np.ma.array(hdul['sci'].data, mask=flat_mask, 
                            fill_value=np.nan)
        hd_min = np.nanmin(hdata)
        hd_max = np.nanmax(hdata)
        hd_mean, hd_median, hd_std = sigma_clipped_stats(hdata)
        hd_cnts, hd_begs = np.histogram(hdata.data,
                                        bins='fd',
                                        range=(hd_min, hd_max) )
        hd_bmid = (hd_begs[:-1] + hd_begs[1:])/2
        
        print(" Masked Array Stats")
        print("\t Min    : {:.3f}".format(hd_min).expandtabs(4))
        print("\t Max    : {:.3f}".format(hd_max).expandtabs(4))
        print("\t Mean   : {:.3f}".format(hd_mean).expandtabs(4))
        print("\t Median : {:.3f}".format(hd_median).expandtabs(4)),
        print("\t StDev  : {:.3f}\n".format(hd_std).expandtabs(4))
        
        fig, axs = plt.subplots(1, 2, figsize=(12,6))
        
        axs[0].imshow(hdata, origin='lower')
        pcm = axs[0].pcolormesh(hdata)
        axs[0].set_title('Masked SCI Array')
        axs[0].annotate("Stats", xy=(10, 210))
        axs[0].annotate("Min       : {:.3f}".format(hd_min), xy=(10, 160))
        axs[0].annotate("Max      : {:.3f}".format(hd_max), xy=(10, 110))
        axs[0].annotate("Median : {:.3f}".format(hd_median), xy=(10, 60))
        axs[0].annotate("StdDev : {:.3f}".format(hd_std), xy=(10, 10))
        
        axs[1].plot(od_bmid, od_cnts, label='Original')
        axs[1].plot(hd_bmid, hd_cnts, label='Masked')
        axs[1].axvline(hd_median)
        axs[1].axvline(hd_min)
        axs[1].axvline(hd_max)
        axs[1].set_yscale('log')
        
        axs[1].legend()
        
        plt.suptitle(f_name)
        plt.colorbar(pcm, ax=axs[0], shrink=0.7)
        plt.tight_layout()
        
        if save is True:
            
            if not os.path.isdir(self.outpath + 'plot/'):
                os.mkdir(self.outpath + 'plot/')
            
            out_name = self.outpath + 'plot/' + f_name.replace('.fits',
                                                              '.png')
            
            plt.savefig(out_name)
        else:
            plt.show()
        
        hdul.close()
        
        return flat_mask
    
    def get_delta_threshold(self, band):
        """
            Function to get the delta threshold to mask point source
            from the input data.
            
        Parameters
        ----------
        band : str
            Name of the MIRI filter/band to get the threshold for.

        Returns
        -------
        The threshold value for the requested band.
        
        Example:
            dthres = get_delta_threshold('F1280W')
        """
        
        if band is None:
            print(" Checking for valid MIRI filter.....")
            if self.band is None:
                print(" MIRI filter undefeined.")
                sys.exit(1)
            else:
                u_band = self.band
        else:
            u_band = band
            
        if not self.is_miri_band(u_band):
            print(" {} is not a valid MIRI filter/band.".format(u_band))
            print(" Exiting ......")
            sys.exit(1)
        
        delta_thresholds = {'F560W': 1, 
                            'F770W': 10,
                            'F1000W': 50,
                            'F1130W': 10,
                            'F1280W': 20,
                            'F1500W': 50,
                            'F1800W': 50,
                            'F2100W': 50,
                            'F2550W': 200}
        
        thres = delta_thresholds[band]
        
        return thres
    
    def generate_flat(self, input_df, mask=None, dthres=None, method="mean",
                      outfile=None, save=False):
        
        input_df = input_df.reindex(columns=[*input_df.columns.tolist(),
                                             'TOTAL_FLAT_MASK',
                                             'TOTAL_RATE_MASK',
                                             'RATE_MEDIAN'], 
                                    fill_value=np.nan)
        
        ratecube = None
        
        outflat = datamodels.FlatModel()
        
        # basic info
        outflat.meta.author = "Sachindev Shenoy"
        outflat.meta.pedigree = "INFLIGHT 2022-04-01 2022-08-20"
        outflat.meta.useafter = "2022-04-01T00:00:00"
        outflat.meta.description = "Flat array from flight data"
        outflat.meta.origin = "STScI"
        outflat.meta.telescope = "JWST"
        outflat.meta.instrument.name = "MIRI"
        outflat.meta.reftype = "Flat"
        # detector info
        outflat.meta.instrument.detector = "MIRIMAGE"
        
        if not self.band is None:
            u_band = self.band
            if not self.is_miri_band(u_band):
                u_band = None
        outflat.meta.instrument.filter = u_band
        
        outflat.meta.instrument.band = "N/A"
        outflat.meta.subarray.name = "GENERIC"
        outflat.meta.exposure.readpatt = "FASTR1"
        outflat.meta.exposure.p_readpatt = "FAST|FASTR1|FASTGRPAVG|FASTGRPAVG16|FASTGRPAVG32|FASTGRPAVG64|FASTGRPAVG8|FASTR100|"
        outflat.meta.subarray.fastaxis = 1
        outflat.meta.subarray.slowaxis = 2
        outflat.meta.subarray.xstart = 1
        outflat.meta.subarray.xsize = 1032
        outflat.meta.subarray.ystart = 1
        outflat.meta.subarray.ysize = 1024
        
        outflat.history.append("File created by taking the sigma clipped " +
                               "".join(method))
        outflat.history.append("    of the normalized rate images: ")
        
        for i, fl in enumerate(input_df['RATEFILE']):
            outflat.history.append(fl)
            
            if self.rate_outpath[-1] != '/':
                self.rate_outpath = self.rate_outpath + '/'
            
            infile = self.rate_outpath+fl
            
            hdul = fits.open(infile)
            
            if u_band is None:
                u_band = hdul[0].header['FILTER']
                if not self.is_miri_band(u_band):
                    print(" {} is not a valid MIRI filter/band.".format(u_band))
                    print(" Skipping {} file.".format(fl))
                    continue
            
            if mask is None:
                mask = np.array(hdul['dq'].data, dtype='bool')
            
            hdul['sci'].data[mask] = np.nan
            hdul['err'].data[mask] = np.nan
            no_fmsk = np.count_nonzero(np.isnan(hdul['sci'].data))
            input_df.loc[i, 'TOTAL_FLAT_MASK'] = no_fmsk
            
            rate_med = np.nanmedian(hdul['sci'].data)
            
            if dthres is None:
                thres = self.get_delta_threshold(u_band)
            else:
                thres = dthres

            t_val = rate_med + thres
            rate_msk = hdul['sci'].data > t_val
            
            hdul['sci'].data[rate_msk] = np.nan
            hdul['err'].data[rate_msk] = np.nan
            no_rmsk = np.count_nonzero(np.isnan(hdul['sci'].data)) - no_fmsk
            input_df.loc[i, 'TOTAL_RATE_MASK'] = no_rmsk
            
            if ratecube is None:
                ratecube = np.zeros((len(input_df['RATEFILE']),
                                     hdul['sci'].data.shape[0],
                                     hdul['sci'].data.shape[1]))
            
            d_mval = np.nanmean(hdul['sci'].data)
            input_df.loc[i, 'RATE_MEDIAN'] = d_mval
            ratecube[i, :, :] = hdul['sci'].data / d_mval
            
            hdul.close()
        
        print(" Using delta threshold of {} for filter {}".format(thres, 
                                                                  u_band))
        # outflat.meta.instrument.filter = u_band
        
        with warnings.catch_warnings(action="ignore"):
            sf_mean, sf_median, sf_std = sigma_clipped_stats(ratecube, 
                                                         mask_value=np.nan,
                                                         sigma_lower=3, 
                                                         sigma_upper=1, 
                                                         axis=0)
        
        if method == "median":
            flat = sf_median
        else:
            flat = sf_mean
        
        flat_unc = sf_std / np.sqrt(len(input_df['RATEFILE'])) #/ np.nanmedian(flat)
        
        
        # add data
        outflat.data = flat.copy()
        outflat.err = flat_unc.copy()
        outflat.dq = mask.copy() #.astype(int)
        
        ### Set DQ flag for pixels that exhibit AD_Floor.
        xpix, ypix = np.where(flat < 0.0)
        
        if len(xpix) >= 1:
            print(f"\n {len(xpix)} pixels had negative values. These pixels")
            print(" are NaN-ed in the SCI & ERR arrays and AD_Floor flag")
            print(" is set the DQ array.") 
            for x, y in zip(xpix, ypix):
                    outflat.data[x, y] = np.nan
                    outflat.err[x, y] = np.nan
                    outflat.dq[x, y] = mask[x, y] + \
                                    datamodels.dqflags.pixel['AD_FLOOR'] + \
                                    datamodels.dqflags.pixel['DO_NOT_USE']
        else:
            print(" All pixels passed the AD_FLOOR test.")
        
        ### Set the DQ mask for the LRS slit region.
        outflat.dq[294:308, 301:351] =  datamodels.dqflags.pixel['NON_SCIENCE']
        
        if save:
            if outfile is None:
                outfile = 'jwst_miri_flat_'+self.band+'_master.fits'
                
            outflat.save(self.outpath+outfile)
   
        return outflat
