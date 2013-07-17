#!/usr/bin/python2

import sys, os, shutil, subprocess

import lib.misc as misc
import lib.configparser as configparser
import lib.message as message

import actions.extract as extract

def check():
	pass
	
def main():
	message.sub_info('Checking')
	check()
	
	message.sub_info('Cleaning')
	extract.clean_work_dirs()