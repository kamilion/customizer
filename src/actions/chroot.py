#!/usr/bin/python2

import sys, os, shutil, subprocess

import lib.misc as misc
import lib.configparser as configparser
import lib.message as message

def check():
	pass
	
def main():
	message.sub_info('Checking')
	check()
	
	message.sub_info('Chrooting')
	misc.chroot_exec(['bash'])