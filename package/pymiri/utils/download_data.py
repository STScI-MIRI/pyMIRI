#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 08:31:16 2024

@author: sshenoy

This is the script uses argparse to get inputs from user and calls
DownloadData class to get MIRI data.
"""

import os
# import sys
import argparse

from pymiri.utils import DownloadData

def main():
    """Main function to call the argparse"""
    parser = argparse.ArgumentParser(description="Download MIRI data " +
                                     "from the MAST archive using " +
                                     "Mashup. Currently works with only " +
                                     "imager data but can be upgraded " +
                                     "to use with other MIRI modes.") 
    parser.add_argument('paramfile', metavar='params', type=str, nargs=1,
                        help="Name of the parmater file that will be used "+
                        "to query the MAST MIRI archive.")
    parser.add_argument('-i', '--inpath', dest='inpath', type=str,
                        action='store', default=os.getcwd(),
                        help="Full path to the input directory where the " +
                        "parameter file in json format is stored. "+ 
                        "Default is current working directory.")
    parser.add_argument('-o', '--outpath', dest='outdir', type=str,
                        action='store', default=None, metavar='outdir1', 
                        help="Name of the output directory where the " +
                        "processed files will be placed. Valid only if " +
                        "-s is set else this flag is ignored. Default is " +
                        "None.")
    parser.add_argument('-t', '--token', dest='token', type=str,
                        action='store', default=None, 
                        help="If you have not set you environment " +
                        "variable MAST_API_TOKEN then you can use this " +
                        "flag to set it.")
    parser.add_argument('-s', '--save', dest='save', action='store_true',
                        default=False, 
                        help="Flag to save intermediate query result files. " +
                        "Default is False. Ignored if -q flag is set.")
    parser.add_argument('-f', '--filename', dest='filename', type=str,
                        action='store', default=None,
                        help="Output filename to save the MAST query " +
                        "tables. Valid of if -s is set else this flag is " +
                        "ignored. Default is None. Ignored if -q flag is set.")
    parser.add_argument('-j', '--jpg', dest='jpg', action='store_true',
                        default=False, 
                        help="Flag to downlad only the preview (*_rate.jpg) " +
                        "file instead of the (*uncal) fits file. Default is " +
                        "False.")
    parser.add_argument('-c', '--counter', dest='count', action='store_true',
                        default=False, 
                        help="All of the query tables are save with " +
                        "current date appended to it. This flag, -c, " +
                        "overides this rule and add a counter instead of" +
                        "a date. Multiple queries with have increasing  " +
                        "count number appened to it. Default is False")
    parser.add_argument('-r', '-rows', dest='rows', type=int, 
                        action='store', default=None,
                        help="Flag to allow number of first r rows from " +
                        "the queryed filtered roducts to downlaod. Default " + 
                        "downloads all the row from the table.")
    parser.add_argument('-q-','--query_file', dest='qfile', type=str,
                        action='store', default=False,
                        help="Flag to use the previously saved filtered " +
                        " product query file to download the data instead " +
                        "of using the PARAM file to query MAST database.")
    parser.add_argument('-p', '--pgroup', dest='pgroup', type=str,
                        action='store', default=None,
                        help="By default this script downloads the UNCAL " +
                        "file. Use this flag to download other product " +
                        "sub-groups like, RATE, CAL etc.")
    
    
    args = parser.parse_args()
    
    gmd = DownloadData.GetMIRIData()
    
    if args.token is None:
        gmd.login2mast()
    else: 
        gmd.login2mast(token=args.token)
    
    params = gmd.read_params(args.paramfile[0], inpath=args.inpath)
    
    if not args.qfile:    
        # SDS: Need to figure out a way to get user input for outfile
        kw_query = gmd.mast_search(params, save=args.save, 
                                   outpath=args.outdir, 
                                   outfile=args.filename,
                                   counter=args.count,
                                   psubgrp=args.pgroup)
    elif args.inpath:
        kw_query = os.path.join(args.inpath, args.qfile)
    else:
        kw_query = args.qfile
    
    if args.jpg:
        download = 'jpg'
    else:
        download = 'fits'
    
    gmd.get_filtered_products(kw_query,
                              kind=download, 
                              outpath=args.outdir,
                              rows=args.rows,
                              psubgrp=args.pgroup)
    
    #gmd.test_args(args)