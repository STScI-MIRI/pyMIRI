#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 10:40:05 2025

@author: sshenoy
"""

"""
This is the script uses argparse to get inputs from user and calls
MakeLRSFalt class to generate MIRI LRS flats.
"""

import os
import sys
import argparse

from ppymiri.lrs import MakeFlat

def main():
    """Main function to call the argparse"""
    parser = argparse.ArgumentParser(description='Genarate MIRI LRS ' +
                                     'Flat for the given input manifest.')
    parser.add_argument('manifest', metavar='manifest', type=str, nargs=1,
                        help='Name of the input manifest listing ' +
                        'the files to process.')
    parser.add_argument('-i', '--inpath', dest='inpath', type=str,
                        action='store', default=os.getcwd(),
                        help='Full path to the input directory where the ' +
                        'input manifest is stored. Default is current ' +
                        'working directory.')
    parser.add_argument('-c', '--config', dest='config', type=str,
                        action='store', default=None,
                        help='Name of the configuration file which lists ' +
                        'all the required input parameters to run the ' +
                        'Detector1Pipeline.')
    parser.add_argument('-o', '--outpath', dest='outdir', type=str,
                        action='store', default=None,
                        help='Name of the output directory where the ' +
                        'processed files will be placed.')
    parser.add_argument('-t', '--model_type', dest='model_type', type=str, 
                        action='store', default='compound', 
                        help='Model type to use: single or compound. '+
                        'Deafult is compound')
    parser.add_argument('-m', '--model_name', dest='model_name', type=str,
                        action='store', default='moffatt',
                        help='Name of the model to use to fir the PSF. '+
                        'Valid model names are: Gaussian or Moffatt. '+
                        'Default is Moffat. This flag is ignored if -t, ' +
                        '--model_type is single.')
    parser.add_argument('-s', '--save', dest='save', action='store_true', 
                        default=False, 
                        help='Flag to save intermediate files. Default ' +
                        'is False.')
    
    args = parser.parse_args()

   
    in_file = args.manifest[0]
    
    mf = MakeFlat.MakeFlat()

 #   params = mf.read_config_file(cfg_file)
    
    if args.inpath[-1] != '/':
        args.inpath = args.inpath + '/'
    
    file_list = mf.read_manifest(in_file, inpath=args.inpath)
    
    if args.outdir is None:
        o_dir = args.inpath + 'proc/' 
    elif args.outdir[-1] != '/':
        o_dir = args.outdir + '/' 
    else:
        o_dir = args.outdir
    
    for f in file_list:
        fit_data = mf.fit_lrs_array(f, save=args.save)
        # bkg_dm = mf.subtract_model_profile(f, 
        #                                    model_param=fit_data, 
        #                                    subtract='moffat', 
        #                                    save=args.save)
        # psf_dm = mf.subtract_model_profile(f, 
        #                                    model_param=fit_data, 
        #                                    subtract='linear', 
        #                                    save=args.save)
    
    print(len(file_list), o_dir, fit_data)#, bkg_dm, psf_dm)
    
    sys.exit()
    