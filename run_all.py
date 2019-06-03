#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script used to convert all notebooks into restructured text
"""

#import nbformat
import argparse
import nbconvert, nbformat
from pyaerocom import const
from nbconvert.preprocessors import ExecutePreprocessor
import fnmatch
import shutil
import os

lustre_avail = const.has_access_lustre
user_server_avail = const.has_access_users_database

# Dictionary that specifies which notebooks (keys) are executed only if 
# a certain condition (value, True / False) is met

SOURCE_DIR = 'notebooks'
OUT_DIR = "rst"

RUN_PREFIX = ['tut', 'add']

RUN_IF = {'add01_intro_time_handling.ipynb': lustre_avail,
          'add02_read_ebas_nasa_ames.ipynb': lustre_avail,
          'add03_ebas_database_browser.ipynb': lustre_avail,
          'add04_stationdata_merging.ipynb': lustre_avail,
          'tut001_setup_userserver.ipynb': user_server_avail,
          'tut00_get_started.ipynb': lustre_avail,
          'tut01_intro_regions.ipynb': lustre_avail,
          'tut02_intro_class_ReadGridded.ipynb': lustre_avail,
          'tut03_intro_class_ReadGriddedMulti.ipynb': lustre_avail,
          'tut04_intro_class_GriddedData.ipynb': lustre_avail,
          'tut05_intro_ungridded_reading.ipynb': lustre_avail,
          'tut06_intro_colocation.ipynb': lustre_avail}

def init_single_notebook_resources(notebook_filename):
    """Step 1: Initialize resources
    
    Note
    ----
    This method was copied and adapted from the nbconvert app main class 
    NbConvertApp in order to instantiate all output in subdirectories

    This initializes the resources dictionary for a single notebook.

    Returns
    -------

    dict
        resources dictionary for a single notebook that MUST include the following keys:
            - unique_key: the notebook name
            - output_files_dir: a directory where output files (not
              including the notebook itself) should be saved
    """
    basename = os.path.basename(notebook_filename)
    notebook_name = basename[:basename.rfind('.')]
    # first initialize the resources we want to use
    resources = {}
    
    resources['unique_key'] = notebook_name
    resources['output_files_dir'] = notebook_name

    return resources

def execute_and_save_notebook(file):
    try:
        print("Executing notebook: {}".format(file))
        with open(file) as f:
            nb = nbformat.read(f, as_version=4)
            
        ep = ExecutePreprocessor(kernel_name="python3")
        ep.timeout = 600
        ep.preprocess(nb, {'metadata': {'path': '.'}})
        
        
        with open(file, 'wt') as f:
            nbformat.write(nb, f)
        print("Success!")
        return True
    except Exception as e:
        print("Failed: {}".format(repr(e)))
        return False
    

if __name__=="__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--noexec', action="store_true",
                        default=False,
                        help=("Don't execute notebooks"))
    
    parser.add_argument('--noconv', default=False, action='store_true',
                        help=("No conversion to rst"))
    
    parser.add_argument('--outdir', default=OUT_DIR, type=str,
                        help="Output directory for converted notebooks")
    
    parser.add_argument('--clearold', action='store_true',
                        default=False,
                        help=("Delete all existing converted notebooks "
                              "in output direcory (i.e. all files and folders "
                              "with trailing number)"))
    
    args = parser.parse_args()
    
    outdir = args.outdir
    
    if not os.path.exists(outdir):
        raise IOError("Specified output directory {} does not exist".format(outdir))
    
    files = []
    skipped = []
    patterns = []
    for prefix in RUN_PREFIX:
        pattern = "{}[0-9]*.ipynb".format(prefix)
        patterns.append(pattern)
        for f in sorted(fnmatch.filter(os.listdir(SOURCE_DIR), pattern)):
            if not f in RUN_IF:
                files.append(f)
            else:
                if RUN_IF[f]:
                    files.append(f)
                else:
                    skipped.append(f)
        
    success, failed = [], []
    conv_success, conv_fail = [], []
    if files:
        if args.clearold:
            ### DELETE OLD NOTEBOOKS (if applicable)
            for pattern in patterns:
                matches = fnmatch.filter(os.listdir(outdir), pattern)
            old = [os.path.join(outdir, x) for x in matches]
            for item in old:
                try:
                    os.remove(item)
                except:
                    shutil.rmtree(item)
                print("Deleted: {}".format(item))
        
        ### RUN ALL NOTEBOOKS
        EXEC = not args.noexec
        EXEC = False
        if EXEC:
            for f in files:
                fp = os.path.join(SOURCE_DIR, f)
                if execute_and_save_notebook(fp):
                    success.append(f)
                else:
                    failed.append(f)
        
        if not args.noconv:                
            converter = nbconvert.RSTExporter()
            
            writer = nbconvert.writers.FilesWriter()
            writer.build_directory = outdir
            
            for f in files:
                fp = os.path.join(SOURCE_DIR, f)
                try:
                    resources = init_single_notebook_resources(fp)
                    (body, resources) = converter.from_file(fp, 
                                                            resources=resources)
            
                    writer.write(body, resources, os.path.splitext(f)[0])
                    conv_success.append(f)
                except Exception as e:
                    conv_fail.append(f)
                    print("Failed to convert {} (Error: {})".format(f, repr(e)))
         
    print('\n\n')
    print('\n--------------\nSKIPPED NOTEBOOK\n--------------\n')
    for f in skipped:
        print(f)
    print()
    
    print('\n--------------\nEXECUTION SUCCESSFUL\n--------------\n')
    for f in success:
        print(f)
    print()
    
    print('\n--------------\nEXECUTION FAILED\n--------------\n')
    for f in failed:
        print(f)
    print()
    if not args.noconv:
        print('\n--------------\nCONVERSION RST SUCCESSFUL\n--------------\n')
        for f in conv_success:
            print(f)
        print()
        print('--------------\nCONVERSION RST FAILED\n--------------\n')
        for f in conv_fail:
            print(f)
        print()
        
        
        
        
        





