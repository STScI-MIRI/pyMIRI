#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 10:50:05 2024

@author: sshenoy
"""

"""
This is the script uses argparse to get inputs from user and calls
MakeFalt class to generate MIRI imager flats.
"""

import os
import sys
import argparse

from . import MakeFlat

def main():
    """Main function to call the argparse"""
    parser = argparse.ArgumentParser(description='Genarate MIRI imager ' +
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
    parser.add_argument('-f', '--filter', dest='filter', type=str,
                        action='store', default=None,
                        help='MIRI Imager filter/band to process. Default ' +
                        'is F560W.')
    parser.add_argument('-o', '--outpath', dest='outdir', type=str,
                        action='store', default=None,
                        help='Name of the output directory where the ' +
                        'processed files will be placed.')
    parser.add_argument('-m', '--mask', dest='mfile', type=str,
                        action='store', default='crds',
                        help='Name of the file whose mask [DQ array] will ' +
                        'be used as masks. Note pixel values not ' +
                        'equal to 0 will be masked.')
    parser.add_argument('-v', '--values', dest='mval', type=float, nargs=2,
                        action='store', default=None, 
                        help='Pixels with values between low and high ' +
                        'value will not be masked.')
    parser.add_argument('-e', '--edge', dest='edge', type=int, 
                        action='store', default=8, 
                        help='Number of edge pixles to mask. Default is 8')
    parser.add_argument('-t', '--threshold', dest='thres', type= float, 
                        action='store', default=None,
                        help='Delta cut threshold used to detect point ' +
                        'like source to mask in the rate file before ' +
                        'combining. Default is 1.0')
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
    
    file_list = mf.read_manifest(in_file, 
                                 inpath=args.inpath)
    
    in_dframe = mf.make_dataframe(file_list)
    
    filt_dframe = mf.filter_dataframe(in_dframe, 
                                      band=args.filter)
    
    if args.outdir is None:
        o_dir = args.inpath + 'proc/' 
    elif args.outdir[-1] != '/':
        o_dir = args.outdir + '/' 
    else:
        o_dir = args.outdir
    
    if args.filter is None:
        outpath = o_dir + filt_dframe['FILTER'][0]
    else:
        outpath = o_dir + args.filter
    
    if args.config is None:
        asdf_file = None
    elif (os.path.isfile(args.config)):
        asdf_file = args.config
    else:
        print(f"File {args.config} does not exist. Using the")
        print("default CRDS parameters for Detector1Pipline.")
        asdf_file = None 
        
    rate_dframe = mf.run_detector1_pipe(filt_dframe, 
                                        outdir=outpath,
                                        asdffile=asdf_file)
    
    #rate_dframe.to_csv('./test_df.csv')
    
    flt_mask = mf.get_mask(args.mfile, 
                           msk_out=args.mval,
                           edge=args.edge,
                           save=args.save)
    
    fdata = mf.generate_flat(rate_dframe, 
                             mask=flt_mask, 
                             dthres=args.thres,
                             save=args.save)
    
    sys.exit()
    