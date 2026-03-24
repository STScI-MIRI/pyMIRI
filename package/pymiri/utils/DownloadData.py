#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 08:43:20 2024

@author: sshenoy

This is the main DownloadData class to get all of the data to 
produce MIRI imager flats.
"""

import os
import sys
import json
from datetime import datetime

# import numpy as np
import pandas as pd
from astroquery.mast import Mast, Observations

class GetMIRIData(object):
    """Class to get MIRI data from MAST"""
    
    def __init__(self):
        self.params = None
        self.inpath = None
        self.filter = None
        self.outpath = os.path.join(os.getcwd(), 'data')
        self.query_dir = os.path.join(self.outpath, 'query_tbls')
        self.token = None
        self.counter = False
    
    
    def check_path(self, inpath, create=False):
        """
        This scripts checks if the provided path exists as a directory on 
        the disk and if not then the users can set a keyword to create it.

        Parameters
        ----------
        inpath : str
            The input path to check

        Returns
        -------
        True if the path exists, esle retuns false.

        """
        
        out_dict = {'check': None,
                    'path': None}
        
        if os.path.isdir(inpath):
            out_dict['check'] = True
            out_dict['path'] = inpath
        else:
            print(" Directory deos not exists:\n {}\n".format(inpath))
            out_dict['check'] = False
            if create:
                os.makedirs(inpath)
                print(" Directory created:\n {}\n".format(inpath))
                out_dict['check'] = True
                out_dict['path'] = inpath
        
        return out_dict
    
    
    def read_params(self, param_file, inpath=None):
        """
        Read the input query parameter json file and format it 
        as a dictionary appropriate for MAST Mashup query.

        Parameters
        ----------
        param_file : str
            Name of the parameter json file.
        inpath : str, optional
            The path to the directory when the param_file is saved. 
            The default is the current directory.

        Returns
        -------
        params : dict
            The output is a dictionary appropriate to use for the 
            MAST mashup query.

        """
        
        # Check the input path
        if inpath is None:
            inpath = os.getcwd()
        else:
            inpath = os.path.abspath(inpath)
            
        chk_pth = self.check_path(inpath)
        if chk_pth['check']:
            self.inpath = inpath
        else:
            sys.exist("Input directory doesn't exists:\n {}".format(inpath))

        infile = os.path.join(self.inpath, param_file)
        if not os.path.isfile(infile):
            sys.exit("Parameter file, {}, does not exist".format(param_file))
        else:
            with open(infile) as pf:
                params = json.load(pf)
        
        for elem in params['filters']:
            if elem['paramName'] == 'filter':
                self.filter = elem['values'][0]
        
        self.params = params
        
        return params
    
    
    def login2mast(self, token=None):
        """
        This script logs in to MAST. If first, looks for the 
        $MAST_API_TOKEN in your environment varible, if it is not found 
        and the keywork argument 'token' is set then it uses this token 
        to log into MAST servises. If no token are found then the script 
        outputs an error.

        Parameters
        ----------
        token : str, optional
            This should be the token that you genrated on the 
            MAST auth website. The default is None.

        Returns
        -------
        None.

        """
        if token is None:
            if 'MAST_API_TOKEN' in os.environ.keys():
                token = os.environ['MAST_API_TOKEN']
                self.token = token
            else:
                msg = """ You have not set the MAST_API_TOKEN
                enviorment variable. If you have alread generated
                a token then please set the MAST_API_TOKEN and run
                this script again or set the token on the command 
                line using the -t flag."""
                sys.exit(msg)
        elif len(token) != 32:
            sys.exit("Your token has incorrect length. \n" +
                     "Please check ....")
        else:
            self.token = token
            
        Observations.login(token=self.token)
        # Observations.login(token=self.token, store_token=True)   
        # session_info = Observations.session_info()
        
        return
    
    def get_out_filename(self, filename, count=None):
        
        if count is None:
            count = self.counter
        
        f_name, f_ext = os.path.splitext(filename)
        
        tm = datetime.now().strftime("%m%d%YT%H%M%S")
        
        if not os.path.exists(filename):
            if not count:
                filename = "{}_{}{}".format(f_name, tm, f_ext)
            return filename
        
        if count:
            i = 1
            new_fname = "{}_{}{}".format(f_name, i, f_ext)
        
            while os.path.exists(new_fname):
                i += 1
                new_fname = "{}_{}{}".format(f_name, i, f_ext)
        else:
            new_fname = "{}_{}{}".format(f_name, tm, f_ext)
        
        return new_fname
    
    
    def save_query_table(self, table_name, opath=None, ofile=None):
        ### Set output directory
        if opath is None:
            qpath = self.query_dir
        else:
            chk_pth = self.check_path(opath, create=True)
            if chk_pth['check']:
                qpath = os.path.join(chk_pth['path'], 'query_tbls')
            else:
                print("There was an issue creating the output " +
                      "directory: {}, please check .....".format(opath))
        
        if not os.path.isdir(qpath):
            os.makedirs(qpath)
        
        ### Set input directory
        if ofile is None:
            outfile = 'jwst_miri_query_table_1.csv'
        elif os.path.splitext(ofile)[1] != '.csv':
            outfile = os.path.splitext(ofile)[0] + '.csv'
        else:
            outfile = ofile
            
        outname = os.path.join(qpath, outfile)
        
        new_oname = self.get_out_filename(outname)

        table_name.write(new_oname, format='ascii.csv')        
       
        return
    
    
    def mast_search(self, params, save=False, outpath=None, 
                    outfile=None, counter=None, psubgrp=None):
        """
        This script queries MAST using the provided input paramter
        file. If the query is successfull then the script returns
        an astropy table containg the query resutls. If outpath or 
        outfile is not provided then the script prints the table 
        head to stdout.

        Parameters
        ----------
        params : str
            This should be the name of the json file that contains 
            the query parameters to send to MAST service request.
        outpath : str, optional
            The name of the output directory to save the query result
            table. The default is None.
        outfile : str, optional
            Name of the output file to save the query result table. 
            The table will be saved in ascii.csv format. The default 
            is None.

        Returns
        -------
        siks_table : astropy.table
            An astropy masked table that contains the results of the
            MAST mashup query.

        """
        
        # Execute the SI Keyword Search
        print(" Starting MAST Query:")
        print(" Executing SI Keyword Query Request ..........")
        service = 'Mast.Jwst.Filtered.Miri'
        kw_search_table = Mast.service_request(service, params)
        
        if counter:
            self.counter = counter
        
        if save:
            if outfile is None:
                outfile = 'service_request_query_table.csv'
                
            self.save_query_table(kw_search_table, 
                                  opath=outpath,
                                  ofile=outfile)
        print(" Query Request Completed.")
        print(" # of Query Resquest rows {}: ".format(len(kw_search_table)))
        print(" Check {} in output directory.".format(outfile))
        
        # Construct obsid and run Observation Search
        if 'filename' in kw_search_table.keys():
            fn = list(set(kw_search_table['filename']))
            ids = list(set(['_'.join(x.split('_')[:-1]) for x in fn]))
        else:
            print(" Column filename not found in the SI keyword ")
            print(" # of Query Resquest rows {}: ".format(len(kw_search_table)))
            print(" search query table. PLease check your param file.")
        
        print(" Executing Criteria Query Request ..........")
        observation_list = Observations.query_criteria(instrument_name='MIRI*', 
                                                       obs_id=ids)
        
        if save:
            outfile = 'observaton_list_table.csv'
            self.save_query_table(observation_list, 
                                  opath=outpath, 
                                  ofile=outfile)
       
        print(" Criteria Query Request Completed.")
        print(" # of Query Resquest rows {}: ".format(len(observation_list)))
        print(" Check {} in output directory.".format(outfile))
        
        # Query for Data Products
        print(" Executing Get Product List Query Request ..........")
        data_products = Observations.get_product_list(observation_list)
        
        if save:
            outfile = 'data_products_table.csv'
            self.save_query_table(data_products, 
                                  opath=outpath,
                                  ofile=outfile)
        
        print(" Get Produc List Query Request Completed.")
        print(" # of Query Resquest rows {}: ".format(len(data_products)))
        print(" Check {} in output directory.".format(outfile))
        
        # Filter the Data Products
        print(" Filtering Products ..........")
        
        if psubgrp is None:
            psgd = ["UNCAL"]
            clvl = 1
        else:
            psgd = [psubgrp.upper()]
            clvl = 2
        
        filtered_product = Observations.filter_products(data_products, 
                                                        calib_level=[clvl], 
                                                        filters=self.filter,
                                                        productSubGroupDescription=psgd)
        
        if save:
            outfile = 'filtered_product_table.csv'
            self.save_query_table(filtered_product, 
                                  opath=outpath,
                                  ofile=outfile)
        
        print(" Filter Product Completed.")
        print(" # of Query Resquest rows {}: ".format(len(filtered_product)))
        print(" Check {} in output directory.".format(outfile))
        
        return filtered_product
    
    
    def get_filtered_products(self, filtered_table, kind=None, 
                              outpath=None, rows=None, psubgrp=None):
        
        if isinstance(filtered_table, str):
            filt_tbl = pd.read_csv(filtered_table)
        else:
            filt_tbl = filtered_table
        
        if rows is not None:
            filt_tbl = filt_tbl[0:rows]
        
        if outpath is None:
            opath = self.outpath
            if not os.path.isdir(opath):
                os.makedirs(opath)
        else:
            chk_pth = self.check_path(outpath, create=True)
            opath = chk_pth['path']
        
        if 'dataURI' in filt_tbl.keys():
            data_urls = pd.DataFrame(filt_tbl['dataURI'], columns=['dataURI'])
            
            if psubgrp is None:
                psgd = "uncal"
            else:
            	psgd = psubgrp.lower()
                
            if kind == 'jpg':
                if psgd == "x1d":
                    get_urls = data_urls['dataURI'].str.replace(psgd+'.fits', psgd+'.png')
                else:
                    get_urls = data_urls['dataURI'].str.replace(psgd+'.fits', psgd+'.jpg')
                opath = os.path.join(opath, 'jpg')
                if not os.path.isdir(opath):
                    os.makedirs(opath)
            elif kind == 'fits':
                get_urls = data_urls['dataURI']
                opath = os.path.join(opath, 'fits')
                if not os.path.isdir(opath):
                    os.makedirs(opath)
            else:
                print(" -j flag has invalid value. -j flag take only " +
                      " two valid values: jpg & fits.")
                
            for url in get_urls:
                out_file = os.path.join(opath, url.split('/')[-1])
                Observations.download_file(url, 
                                           local_path=out_file, 
                                           cache=True)
        else:
            print(" dataURI column not found in the filtered produt table.")
           
        return
    

    def test_args(self, args):
        print("This is test to ensure successful completion of GetMIRIData " +
              "Class.")
        print(args._get_kwargs())
