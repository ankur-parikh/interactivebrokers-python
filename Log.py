# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 02:54:48 2020

@author: smit
"""
from os import path
from global_variables import GlobalVariables
from datetime import datetime 
def WriteLog(method,error):
    try:
        if(path.exists(GlobalVariables.ExceptionLog) == False):
            file = open(GlobalVariables.ExceptionLog,"w+")
            file.write("Date : ",datetime.now() ,"\n")
            file.write("Method : ",method ,"\n")
            file.write("Errror : ",error ,"\n")
            file.write("-------------------------------------------------------------------------\n")
            file.close()
        if(path.exists(GlobalVariables.ExceptionLog) == True):
            file.write("Date : ",datetime.now() ,"\n")
            file.write("Method : ",method ,"\n")
            file.write("Errror : ",error ,"\n")
            file.write("-------------------------------------------------------------------------\n")
    except Exception as ex:
        print("Error Log.patternLog : ",ex)