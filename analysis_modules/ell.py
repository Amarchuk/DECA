#!/usr/bin/python
# IRAF ellipse fitting
import random as random_number
import sys
import math
import numpy as np
from scipy import stats
import scipy as sp
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.gridspec as gridspec
from matplotlib.ticker import NullFormatter
from numpy import *
from pylab import *
import os
import shutil
import subprocess
from os.path import exists
import fileinput
import pyfits
import re

tmp_out = sys.stdout

DECA_PATH = os.path.split(os.path.dirname(__file__))[0]

sys.path.append(DECA_PATH)
sys.path.append(DECA_PATH + '/ini_modules')
sys.path.append(DECA_PATH + '/analysis_modules')
sys.path.append(DECA_PATH + '/output_modules')
sys.path.append(DECA_PATH + '/prep_modules')

import setup
import psf
fsize=24

def crea_ell(file_in,xc,yc,step,minsma,maxsma,ell_file):
	f = open("ell.cl", "w") 
	sys.stdout = f

	print "# Script: ellipse"
	print "!rm -f ellipse.txt"
	print "stsdas"
	'''
	print "fitsio"
	print "set imtype=hhh"
	print "strfits %s \"\" gal.hhh xdim=yes oldiraf=yes force=yes" % (file_in)
	print "bye"
	'''
	print "analysis"
	print "isophote"
	print "geompar.linear=yes"
	print "geompar.step=%.1f" % (step) 
	print "geompar.minsma=%.1f" % (minsma)
	print "geompar.maxsma=%.1f" % (maxsma)
	print "geompar.x0=%.3f" % (xc)
	print "geompar.y0=%.3f" % (yc)
	#print "controlpar.soft=yes"
	print "ellipse %s gal.tab" % (file_in)
	print "tprint gal.tab pwidth=600 plength=1000 > %s" % (ell_file)
	print "!rm -f gal.tab"
	print "logout"

	sys.stdout = tmp_out
	f.close()

def plot_PA(PA,errPA,a,pix2sec):
	plt.errorbar(a*pix2sec, fabs(PA),yerr=errPA,fmt='o',color='black', markersize=3)
	#ylim(25,13)
	plt.xlabel(r'r (arcsec)', fontsize=fsize)
	plt.ylabel(r'PA (deg)', fontsize=fsize)
	#pic = name + '.png'
	#savefig(pic,bbox_inches=0)	
	plt.show()

def plot_ell(ell,errell,a,pix2sec):
	plt.errorbar(a*pix2sec, fabs(ell),yerr=errell,fmt='o',color='black', markersize=3)
	#ylim(25,13)
	plt.xlabel(r'r (arcsec)', fontsize=fsize)
	plt.ylabel(r'$\epsilon$ ', fontsize=fsize)
	#pic = name + '.png'
	#savefig(pic,bbox_inches=0)	
	plt.show()

def plot_B4(B4,errB4,a,pix2sec):
	plt.errorbar(a*pix2sec, B4,yerr=errB4,fmt='o',color='black', markersize=3)
	#ylim(25,13)
	plt.xlabel(r'r (arcsec)', fontsize=fsize)
	plt.ylabel(r'B$_4$ ', fontsize=fsize)
	#pic = name + '.png'
	#savefig(pic,bbox_inches=0)	
	plt.show()

def plot_iso(inten,inten_err,PA,errPA,ell,errell,B4,errB4,a,pix2sec,m0,FWHM,rmax):
	mag = m0 - 2.5*log10(inten)
	mag_err = fabs((2.5/log(10.0)) * inten_err/inten)

	f= figure(0,figsize=(4,10))

	gs = gridspec.GridSpec(3, 1,width_ratios=[1,3])
	gs.update(left=0.25, right=3.00, hspace=0.0)

	ax1 = plt.subplot(gs[0])
	ax2 = plt.subplot(gs[1])
	ax3 = plt.subplot(gs[2])

	ax1.errorbar(a*pix2sec, fabs(PA),yerr=errPA,fmt='o',color='black', markersize=3)
	#ax1.set_xlabel(r'r (arcsec)', fontsize=fsize)
	ax1.set_ylabel(r'PA (deg)', fontsize=fsize)
	#ax1.set_title(name,ha='left',fontsize=fsize,color='red')

	ax2.errorbar(a*pix2sec, fabs(ell),yerr=errell,fmt='o',color='black', markersize=3)
	#ax2.set_xlabel(r'r (arcsec)', fontsize=fsize)
	ax2.set_ylabel(r'$\epsilon$ ', fontsize=fsize)
	ax2.set_ylim(np.min(fabs(ell)-fabs(errell)-0.06), np.max(fabs(ell)+fabs(errell)+0.06))

	ax3.errorbar(a*pix2sec, B4,yerr=errB4,fmt='o',color='black', markersize=3)
	ax3.set_xlabel(r'r (arcsec)', fontsize=fsize)
	ax3.set_ylabel(r'B$_4$ ', fontsize=fsize)
	xticklabels = ax1.get_xticklabels()+ax2.get_xticklabels()
	setp(xticklabels, visible=False)
	plt.savefig("ell.png", transparent = False)

	f1 = figure(1, figsize=(10,10))


	tck = interpolate.splrep(np.array(a*pix2sec),np.array(inten),s=0)
	r_interp = np.arange(min(a*pix2sec),rmax,0.5)
	#r_interp = np.array(a*pix2sec)
	I_interp = interpolate.splev(r_interp,tck,der=0)
	mag_interp = m0 - 2.5*log10(I_interp)
	plt.plot(r_interp,mag_interp,'o',color='grey',markersize=3)



	Inten_deconv = psf.deconv_moffat(I_interp,r_interp,fwhm=FWHM)
	#Inten_deconv = psf.deconv_gauss(I_interp,r_interp,fwhm=FWHM)
	Mag_deconv = m0 - 2.5*log10(Inten_deconv)
	r_deconv = []
	for mm in range(len(Mag_deconv)):
		r_deconv.append(r_interp[mm])

	plt.plot(r_deconv,Mag_deconv,'*',color='grey',lw=3)

	plt.errorbar(a*pix2sec,mag,yerr=mag_err,fmt='o',color='red', markersize=5)

	#xlim(-nx/2,nx/2)
	ylim(max(mag)+max(mag_err)+0.3,min(mag)-max(mag_err)-1.)
	plt.xlabel(r'r (arcsec)', fontsize=fsize)
	plt.ylabel(r'$\mu$ (mag arcsec$^{-2}$)', fontsize=fsize)
	plt.savefig("azim_aver.png", transparent = False)

def main_ell(file_in,xc,yc,step,minsma,maxsma,m0,pix2sec,FWHM,rmax,noise,ell_file='ellipse.txt'):
	#os.remove(r"ell.cl")
	#os.remove(r"ellipse.txt")
	import time
	#print 'MAXSMA',maxsma
	#time.sleep(60)

	crea_ell(file_in,xc,yc,step,minsma,maxsma,ell_file)
	#shutil.copy(r"/home/aleksandr/diser/TEST_GALAXY/prog/modules/ellipse/ell.cl",r"/home/aleksandr/diser/TEST_GALAXY/ell.cl")
	os.chmod(r"ell.cl",0777)
	subprocess.call("cl < ell.cl -o", shell=True)

	'''
	import time
	import multiprocessing

	def ell_running():
		subprocess.call("cl < ell.cl -o", shell=True)

	downloader = multiprocessing.Process(target=ell_running)
	downloader.start()
	timeout = 0.5
	time.sleep(timeout)
	downloader.terminate()

	#http://pastebin.com/89Wfduxq
	'''
	sma,inten,inten_err,ell,errell,PA,errPA,x0,y0,B4,errB4 = loadtxt(ell_file, usecols=[1,2,3,6,7,8,9,10,12,33,34], unpack=True, skiprows = 6, dtype='str')

	for k in range(len(sma)):
		if sma[k]=='INDEF': sma[k]=0
		if inten[k]=='INDEF': inten[k]=0
		if inten_err[k]=='INDEF': inten_err[k]=0
		if ell[k]=='INDEF': ell[k]=0
		if errell[k]=='INDEF': errell[k]=0
		if PA[k]=='INDEF': PA[k]=0
		if errPA[k]=='INDEF': errPA[k]=0
		if x0[k]=='INDEF': x0[k]=0
		if y0[k]=='INDEF': y0[k]=0
		if B4[k]=='INDEF': B4[k]=0
		if errB4[k]=='INDEF': errB4[k]=0
	sma = np.array(sma,dtype='float')
	inten = np.array(inten,dtype='float')
	inten_err = np.array(inten_err,dtype='float')
	ell = np.array(ell,dtype='float')
	errell = np.array(errell,dtype='float')
	PA = np.array(PA,dtype='float')
	errPA = np.array(errPA,dtype='float')
	x0 = np.array(x0,dtype='float')
	y0 = np.array(y0,dtype='float')
	B4 = np.array(B4,dtype='float')
	errB4 = np.array(errB4,dtype='float')


	#plot_PA(PA,errPA,sma,pix2sec)
	#plot_ell(ell,errell,sma,pix2sec)
	#plot_B4(B4,errB4,sma,pix2sec)
	plot_iso(inten,inten_err,PA,errPA,ell,errell,B4,errB4,sma,pix2sec,m0,FWHM,rmax)

	if setup.deca_del_contam==0:
		import del_stars
		del_stars.delete(xc,yc,xc,yc,sma,inten,inten_err,sma,sma*(1.-ell),PA,noise)


def read_ell(ell_file,radius,step):
	sma,inten,inten_err,ell,errell,PA,errPA,x0,y0,B4,errB4 = loadtxt(ell_file, usecols=[1,2,3,6,7,8,9,10,12,33,34], unpack=True, skiprows = 6, dtype='str')

	for k in range(len(sma)):
		if sma[k]=='INDEF': sma[k]=99999.
		if inten[k]=='INDEF': inten[k]=99999.
		if inten_err[k]=='INDEF': inten_err[k]=99999.
		if ell[k]=='INDEF': ell[k]=99999.
		if errell[k]=='INDEF': errell[k]=99999.
		if PA[k]=='INDEF': PA[k]=99999.
		if errPA[k]=='INDEF': errPA[k]=99999.
		if x0[k]=='INDEF': x0[k]=99999.
		if y0[k]=='INDEF': y0[k]=99999.
		if B4[k]=='INDEF': B4[k]=99999.
		if errB4[k]=='INDEF': errB4[k]=99999.
	sma = np.array(sma,dtype='float')
	inten = np.array(inten,dtype='float')
	inten_err = np.array(inten_err,dtype='float')
	ell = np.array(ell,dtype='float')
	errell = np.array(errell,dtype='float')
	PA = np.array(PA,dtype='float')
	errPA = np.array(errPA,dtype='float')
	x0 = np.array(x0,dtype='float')
	y0 = np.array(y0,dtype='float')
	B4 = np.array(B4,dtype='float')
	errB4 = np.array(errB4,dtype='float')


	'''
	kk = 0
	while kk<=2:
		Ell = []
		BB4 = []
		for k in range(len(sma)):
			if sma[k]>=radius-step and sma[k]<=radius+step and ell[k]!=0 and B4[k]!=0:
				Ell.append(ell[k])
				BB4.append(B4[k])
				kk = kk + 1
		step = step+1
	
			
		
	if type(Ell)==np.ndarray:
		ellip = mean(Ell)
		bb4 = mean(BB4)
	else:
		ellip = median(Ell)
		bb4 = median(BB4)
	'''


	BB4 = []
	for k in range(len(sma)):
		if B4[k]!=99999. and sma[k]<radius*2.:
			BB4.append(B4[k])


	ellip = 0.
	return ellip,median(BB4)


def rmax_bar(rmax,ell_file='ellipse.txt'):
	sma,inten,inten_err,ell,errell,PA,errPA,x0,y0,B4,errB4 = loadtxt(ell_file, usecols=[1,2,3,6,7,8,9,10,12,33,34], unpack=True, skiprows = 6, dtype='str')

	for k in range(len(sma)):
		if sma[k]=='INDEF': sma[k]=99999.
		if inten[k]=='INDEF': inten[k]=99999.
		if inten_err[k]=='INDEF': inten_err[k]=99999.
		if ell[k]=='INDEF': ell[k]=99999.
		if errell[k]=='INDEF': errell[k]=99999.
		if PA[k]=='INDEF': PA[k]=99999.
		if errPA[k]=='INDEF': errPA[k]=99999.
		if x0[k]=='INDEF': x0[k]=99999.
		if y0[k]=='INDEF': y0[k]=99999.
		if B4[k]=='INDEF': B4[k]=99999.
		if errB4[k]=='INDEF': errB4[k]=99999.
	'''
	sma = np.array(sma,dtype='float')
	inten = np.array(inten,dtype='float')
	inten_err = np.array(inten_err,dtype='float')
	ell = np.array(ell,dtype='float')
	errell = np.array(errell,dtype='float')
	PA = np.array(PA,dtype='float')
	errPA = np.array(errPA,dtype='float')
	x0 = np.array(x0,dtype='float')
	y0 = np.array(y0,dtype='float')
	B4 = np.array(B4,dtype='float')
	errB4 = np.array(errB4,dtype='float')
	'''

	ELL = []
	PAA = []
	R = []


	for k in range(len(sma)):
		if float(ell[k])!=99999. and float(PA[k])!=99999. and float(sma[k])<rmax/3. and float(sma[k])>4.:
			ELL.append(float(ell[k]))
			PAA.append(float(PA[k]))
			R.append(float(sma[k]))

	#print 'rmax!',rmax,R
	#print ELL
	#print PAA
	#exit()

	#print R[ELL.index(max(ELL))],R[PAA.index(min(PAA))]
	#exit()
	rmaxBAR = min([R[ELL.index(max(ELL))],R[PAA.index(min(PAA))]])
	#print 'rmax!',rmaxBAR
	#exit()
	return float(rmaxBAR)
	

