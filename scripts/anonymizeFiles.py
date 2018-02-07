'''
Program to anonymize the metadata of a directory of patient x-rays
Hillary Elrick
CISC 499
Jan 22, 2018
'''

import errno
import os
from os.path import join
import shutil
import dicom

def main():
    path = input("Please enter the file or directory path: ")
    new_path = input("Please enter the destination path to an empty directory for the anonymized files: ")
    
    #make a copy of the source directory and its folders and files
    try: 
        shutil.copytree(path, new_path)
    except OSError as e:
        if e.errno == errno.ENOTDIR:
            shutil.copy(path, new_path)
        else:
            print('Problem making copy of source directory')
            print(e.errno)
    
    #walks through the directory tree
    prefix = len(new_path) + 1

    #TODO: consider adding for loop that skims the top-level directories to get a list of 'patients' (i.e. P1, P2, etc.)

    patient_folders = []

    for root, dirs, files in os.walk(new_path):
        short_dirname = root[prefix:]

        #note: this is a hack! fix later
        if ("/" not in short_dirname):
            patient_folders.append(short_dirname)
        if(short_dirname != ''):
            print('In File: ' + short_dirname)

        for name in files:
            if(name != '.DS_Store' and name != '.DS_Store.dcm'):
                print(name)
                print(join(root,name))
                ds = dicom.read_file(join(root,name))
                print ds.PatientsName
                if(ds.PatientsSex == 'M'):
                    ds.PatientsName = 'JohnDoe_' + patient_folders[-1]
                    ds.save_as(join(root,name))
                else:
                    ds.PatientsName = 'JaneDoe_' + patient_folders[-1]
                    ds.save_as(join(root,name))
                print ds.PatientsName


main()

