#!/usr/bin/python
# -*- coding:  cp1251 -*-

#*** Common modules ***
import sys
import math
import numpy as np
from scipy import stats
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.patches as patches
import matplotlib.path as path
from matplotlib.ticker import NullFormatter
from numpy import *
from pylab import *
import os
import shutil
import subprocess
import random
import time
import pyfits
import re
from scipy import special
#from pyraf import iraf

DECA_PATH = os.path.split(os.path.dirname(__file__))[0]

sys.path.append(DECA_PATH)
sys.path.append(DECA_PATH + '/ini_modules')
sys.path.append(DECA_PATH + '/analysis_modules')
sys.path.append(DECA_PATH + '/output_modules')
sys.path.append(DECA_PATH + '/prep_modules')

#*** Colour fonts ***
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

#*** USED DECA MODULES ***
import sextr
import changer
import psf
import image 
#import surveys
import ell
import GALFIT
import INITIALS
import out
import res
import sky_est
import INITIALS_edge_on
import setup
#import superellipse
#import edge_soph
#import iter2
#import bulge_pic
import constraints
#import fitting

tmp_out = sys.stdout
import setup

file_out_ini = setup.file_out_ini
file_inimodels_txt = setup.file_inimodels_txt
way_ini = setup.way_ini
one_dec = setup.one_dec

file_weight = 'weight.fits'
file_constraints = 'constr.txt'
file_galfit_input = 'input.txt'
file_field = 'field.fits'
file_psf_field = 'psField.fit'	# for SDSS
file_field1 = 'field1.fits'
file_field2 = 'field2.fits'
file_gal = 'galaxy.fits'
file_sex_field = 'field.cat'
file_sex_galaxy = 'galaxy.cat'
file_gal_clean = 'galaxy_clean.fits'
file_gal_clean_new = 'galaxy_clean1.fits'
file_segm = 'segm.fits'
file_badpix = 'badpix.txt'
file_inter = 'interact.cat'
file_psf = 'psf.fits'
file_psf_model = 'psf_model.fits'
file_nonpar = 'nonpar.txt'
file_galfit_outimage = 'galfit_out.fits'
file_out_txt = setup.file_out_txt

C1 = setup.C1
C2 = setup.C2
Ccr = setup.Ccr
El_cr = setup.El_cr
ellip_cr = setup.ellip_cr

def magBulge_meb (reb,magBulge,n):
	nu = 1.9987*n-0.3267
	fn = n*special.gamma(2.0*n)/(nu**(2.0*n))
	m0b = magBulge + 2.5*(log10(fn) + log10(2.0*math.pi*reb*reb))
	meb = m0b+1.0857*nu
	return meb

def magDisk_m0d(magDisk,h):
	return magDisk + 2.5*log10(2.*math.pi) + 5.*log10(h)



def way_corrs(model,flux_radius,mag_auto,C31,ellip,a_image,FWHM,pix2sec):
	reb0 = 99999.
	meb0 = 99999.
	m0d0 = 99999.
	magBul0 = 99999.
	magDisk0 = 99999.
	n0 = 99999.
	ellb0 = 99999.
	cb0 = 99999.
	h0 = 99999.
	z00 = 99999.
	elld0 = 99999.
	cd0 = 99999.
	rtr0 = 99999.

	if model=='ser': 
		reb0 = flux_radius
		magBul0 = mag_auto
		if C31>Ccr:	n0 = 3.8
		else:	n0 = 2.
		ellb0 = ellip
		cb0 = 0.
		meb0 = magBulge_meb (reb0*pix2sec,magBul0,n0)

	if model=='exp':
		h0 = flux_radius/1.678
		magDisk0 = mag_auto
		#m0d0 = 99999.
		z00 = 99999.
		elld0 = ellip
		cd0 = 0.
		rtr0 = a_image
		m0d0 = magDisk_m0d(magDisk0,h0*pix2sec)

	if model=='edge':
		h0 = flux_radius/1.678
		magDisk0 = mag_auto
		#m0d0 = 99999.
		z00 = h0/4.
		elld0 = 99999.
		cd0 = -1.
		rtr0 = a_image
		m0d0 = magDisk_m0d(magDisk0,h0*pix2sec) + 2.5*log10(z00/h0)	

	if model=='exp+ser':
		#reb0 = 2.*FWHM
		reb0 = 0.056*a_image*(C31-2.)
		def BT_c31(C31):
			return 0.18*(C31-2.5)

		if C31>Ccr:
			n0 = 3.0
			magBul0 = mag_auto - 2.5*log10(BT_c31(C31))
			magDisk0 = mag_auto -2.5*log10(1.-BT_c31(C31))
		else:
			n0 = 1.5
			magBul0 = mag_auto - 2.5*log10(BT_c31(C31))
			magDisk0 = mag_auto -2.5*log10(1.-BT_c31(C31))
			
		ellb0 = 0.
		cb0 = 0.
		h0 = a_image/3.4
		z00 = 99999.
		elld0 = ellip
		cd0 = 0.
		rtr0 = a_image
		meb0 = magBulge_meb (reb0*pix2sec,magBul0,n0)
		m0d0 = magDisk_m0d(magDisk0,h0*pix2sec)

	if model=='edge+ser':
		def BT_ell(x):
			A = 0.493
			B = 0.871
			C = 0.830
			return A*log10(-x+B) + C


		if ellip<El_cr:
			n0 = 3.0
			magBul0 = mag_auto - 2.5*log10(BT_ell(ellip))
			magDisk0 = mag_auto -2.5*log10(1.-BT_ell(ellip))
		else:
			n0 = 1.5
			magBul0 = mag_auto - 2.5*log10(BT_ell(ellip))
			magDisk0 = mag_auto -2.5*log10(1.-BT_ell(ellip))
			
		ellb0 = 0.
		cb0 = 0.
		h0 = a_image/5.
		z00 = h0/4.
		reb0 = h0*0.3
		elld0 = 99999.
		cd0 = -1.
		rtr0 = a_image
		meb0 = magBulge_meb (reb0*pix2sec,magBul0,n0)
		m0d0 = magDisk_m0d(magDisk0,h0*pix2sec) + 2.5*log10(z00/h0)
	#return m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0
	return m0d0,99999.,h0,z00,elld0,cd0,rtr0,meb0,99999.,reb0,n0,ellb0,cb0

'''
def galfit(model,PA,FWHM,pix2sec):
	# GALFIT decomposition
	trunc = 1
	constraints.constr(file_constraints,model,trunc,FWHM,pix2sec)	# Creating constraints file
	print bcolors.OKBLUE+ 'GALFIT decomposition ...' + bcolors.ENDC
	#print >> ff, 'GALFIT decomposition ...'
	PA = image.pa(PA)

	hdulist = pyfits.open(file_gal_clean)
	scidata = hdulist[0].data
	ny,nx = scidata.shape


	crush = GALFIT.dec_galfit1(file_galfit_input, file_gal_clean, file_galfit_outimage,'psf.fits', file_badpix,file_constraints, m0 - 2.5*log10(EXPTIME), pix2sec, nx, ny, xc, yc, m0d=m0d0,h=h0,z0=z00,PAd=90.,elld=elld0,cd=cd0,meb=meb0,reb=reb0,n=n0,ellb=ellb0,PAb=90.,cb=cb0,sky_level=SKY_LEVEL,rtr=rmax0,file_sigma=file_weight)
	if crush==0:	xc_d,yc_d,m0_d,h,q_d,z0,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,chi2 = res.results(galaxy_name,model,file_galfit_outimage,file_out_txt,file_out_pdf,filter_name,colour_name,colour_value,Aext,z,pix2sec,m0,D,tables='tog',gal_number=0,out=1)
	return status
'''


def def_model(ellip,C31,cod):
	model = []
	if ellip>ellip_cr:
		model.append('edge+ser')
		if C31<C1:
			model.append('edge')
		if cod=='1':
			model.append('ser')		
			
	elif ellip<=ellip_cr:
		model.append('exp+ser')
		if C31<C1:	
			model.append('exp')
		if C31>C2:	
			model.append('ser')
		if cod=='1' and C31<=C2:
			model.append('ser')			
	return model

def filters(f):
	if f=='J' or f=='H' or f=='K' or f=='Ks' or f=='NIR':
		return 0
	else:
		return 1


def ini_load(i,pix2sec):
		# !!! Surface Brightness should be given in mag/arcsec^2 and sizes in arcsec !!!
		# Then sizes will be transformed in pixels!!! 
		if os.path.exists('initials.py')==False and os.path.exists('initials.dat')==False:
			sys.exit(bcolors.FAIL+ 'The input file with initials is not found!'+ bcolors.ENDC)
		elif os.path.exists('initials.py')==True:
			print bcolors.OKBLUE+ 'The program is using your initial parameters from the file initials.py!' + bcolors.ENDC
			import initials

			m0d0 = initials.m0_d
			magDisk0 = initials.magDisk
			if initials.h_d!=99999.:
				h0 = (initials.h_d)/pix2sec
			else:
				h0 = 99999.
			if initials.z0!=99999.:
				z00 = (initials.z0)/pix2sec
			else:
				z00 = 99999.
			elld0 = initials.ell_d
			cd0 = initials.c_d
			if initials.r_tr!=99999.:
				rtr0 = (initials.r_tr)/pix2sec
			else:
				rtr0 = 99999.
		
			meb0 = initials.me_bul
			magBul0 = initials.magBul
			if initials.re_bul!=99999.:
				reb0 = (initials.re_bul)/pix2sec
			else:
				reb0 = 99999.
			n0 = initials.n_bul
			ellb0 = initials.ell_bul
			cb0 = initials.c_bul
			return m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0


		elif os.path.exists('initials.dat')==True:
			print bcolors.OKBLUE+ 'The program is using your initial parameters from the file initials.dat!' + bcolors.ENDC
			#*** PARAMETERS FROM THE INPUT FILE deca_input.dat as a list of objects ***
			with open('initials.dat', 'r') as f:
				lines = f.readlines()
				num_lines = len([l for l in lines if l.strip(' \n') != ''])
			n_it = num_lines

			#	0	1	2	3	4	5	6	7	8	9	10	11	12	13	14
			#	#	filter	S0d	mag_d	h_d	z0_d	ell_d	c_d	r_tr	me_bul	mag_bul	re_bul	n_bul	ell_bul	c_bul	

			m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0 = loadtxt('initials.dat', usecols=[2,3,4,5,6,7,8,9,10,11,12,13,14],dtype=float, unpack=True,skiprows=0)
			numbs = loadtxt('initials.dat', usecols=[0],dtype=int, unpack=True,skiprows=0)
			filts = loadtxt('initials.dat', usecols=[1],dtype=str, unpack=True,skiprows=0)

			if h0[i]!=99999.:
				h0[i] = h0[i]/pix2sec
			
			if z00[i]!=99999.:
				z00[i] = z00[i]/pix2sec

			if rtr0[i]!=99999.:
				rtr0[i] = rtr0[i]/pix2sec

			if reb0[i]!=99999.:
				reb0[i] = reb0[i]/pix2sec

			return m0d0[i],magDisk0[i],h0[i],z00[i],elld0[i],cd0[i],rtr0[i],meb0[i],magBul0[i],reb0[i],n0[i],ellb0[i],cb0[i]



			




def  main(ff_log,number,xc,yc,kron_r,flux_radius,mag_auto,a_image,b_image,PA,NOISE,pix2sec,m0,FWHM,EXPTIME,ini_use,find_model,model,ellip,C31,sky_level,file_out_txt,file_out_pdf,filter_name,colour_name,colour_value,Aext,z,D,galaxy_name,find_psf,rmax,mode):
	if not os.path.exists("./pics/%i" % (number)):
		os.makedirs("./pics/%i" % (number))


	#print m0,FWHM,NOISE,ellip,C31
	#exit()

	hdulist = pyfits.open(file_gal_clean)
	scidata = hdulist[0].data
	ny,nx = np.shape(scidata)


	ff = open('models.txt', 'w')
	f_ini = open('ini.txt', 'w')
	if find_model=='NO':
		if model=='NO' or (model!='exp' and model!='exp+ser' and model!='ser' and model!='edge' and model!='edge+ser'):
			sys.exit(bcolors.FAIL+ 'Specify the input model!'+ bcolors.ENDC)
		cod = '0'
		model1 = def_model(ellip,C31,cod)
		if len(model1)==2:
			model2=[]
			model2.append(model)
			model2.append(model1[0])
			model2.append(model1[1])
			model = model2
			cod = '1'
		else:
			model2=[]
			if model=='exp':
				model2.append(model)
				model2.append('exp+ser')
				model2.append('ser')
			elif model=='ser':
				model2.append(model)
				model2.append('exp+ser')
				model2.append('edge+ser')
			elif model=='exp+ser':
				model2.append(model)
				model2.append('exp')
				model2.append('ser')
			elif model=='edge+ser':
				model2.append(model)
				model2.append('edge')
				model2.append('ser')
			elif model=='edge':
				model2.append(model)
				model2.append('edge+ser')
				model2.append('ser')
			model = model2
			
	else:
		cod = '1'
		model = def_model(ellip,C31,cod)

	status=1
	Model = model[0]
	k = 0
	way = way_ini	
	good = 1


	k_iter = 1

	if mode==4:	good=0
	NIR = filters(filter_name) # NIR = 0
	NIR = 0

	print 'Models to be checked: %s' % (model)
	print >>ff_log, 'Models to be checked: %s' % (model)

	while (status!=0 and k<len(model))  or (k<len(model) and cod=='1'):
		print 'Model %s is now considering!' % (Model)
		if ini_use=='NO':
			if way==2:
				try:
					print 'Way to find initial parameters: 2'
					print >>ff_log, 'Way to find initial parameters: 2'
					if Model=='exp' or Model=='exp+ser' or Model=='ser':
						m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0 = INITIALS.ini_prof('azim',xc,yc,PA,m0,pix2sec,NOISE,a_image*kron_r,FWHM,Model,ellip,C31)
						good = 0
						#print '!!!!!!!!',xc,yc,PA,m0,pix2sec,NOISE,a_image*kron_r,FWHM,Model,ellip,C31
						
					elif Model=='edge' or Model=='edge+ser':
						if NIR==0:
							m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0,xc,yc,incl = INITIALS_edge_on.main_edge(file_gal_clean,xc,yc,kron_r,a_image,b_image,NOISE,pix2sec,m0,FWHM,Model,ellip,C31,NIR)
							good = 0
						else:
							good = 1

						#m0d1,magDisk1,h1,z01,elld1,cd1,rtr1,meb0,magBul0,reb0,n0,ellb0,cb0 = INITIALS.ini_prof('azim',xc,yc,PA,m0,pix2sec,NOISE,a_image*kron_r,FWHM,Model,ellip,C31)


						
						
				except:
					print bcolors.FAIL+ 'This way failed!'+ bcolors.ENDC
					print >>ff_log, '  This way failed!'
					good=1
					NIR = 1
				

			if way==3 or good!=0:
				try:
					print 'Way to find initial parameters: 3'
					print >>ff_log, 'Way to find initial parameters: 3'
					if Model=='exp' or Model=='exp+ser' or Model=='ser':
						m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0 = INITIALS.ini_prof('cut',xc,yc,PA,m0,pix2sec,NOISE,a_image*kron_r,FWHM,Model,ellip,C31)
						good = 0
					elif Model=='edge' or Model=='edge+ser':
						#m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0 = INITIALS.ini_prof('azim',xc,yc,PA,m0,pix2sec,NOISE,a_image*kron_r,FWHM,Model,ellip,C31)
						m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0,xc,yc,incl = INITIALS_edge_on.main_edge(file_gal_clean,xc,yc,kron_r,a_image,b_image,NOISE,pix2sec,m0,FWHM,Model,ellip,C31,NIR)
						good = 0
				except:
					good=1
					print bcolors.FAIL+ 'This way failed!'+ bcolors.ENDC
					print >>ff_log, '  This way failed!'
					#exit()
			if way==4 or good!=0:
				print 'Way to find initial parameters: 4'
				print >>ff_log, 'Way to find initial parameters: 4'
				m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0 = way_corrs(Model,flux_radius,mag_auto,C31,ellip,a_image*kron_r,FWHM,pix2sec)
				#print m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0,'okkkkkkkk'
				good = 0

		else:
			print 'Given initial parameters will be used!'
			print >>ff_log, 'Given initial parameters will be used!'
			way = 1
			cod = '0'
			m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0 = ini_load(number-1,pix2sec)

		if mode==4:
			if not os.path.exists("%s" % (file_inimodels_txt)):
				ff_ini = open(file_inimodels_txt,'w')
				print >>ff_ini, '#\tm0d0\tmd0\th0\tz0\telld0\tcd0\trtr0\tmeb0\tmbul0\treb0\tn0\tellb0\tcb0\tmodel\tway'
				print >>ff_ini, '\tmas\tmag\tarcsec\tarcsec\t\t\tarcsec\tmas\tmag\tarcsec\t\t\t\t\t\t'
				ff_ini.close()

			ff_ini = open(file_inimodels_txt, 'a')
			print >>ff_ini, '%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s\t%s' % (number,m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0,Model,way)
			ff_ini.close()
			exit()

		if mode==5:
			if not os.path.exists("%s" % (file_inimodels_txt)):
				ff_ini = open(file_inimodels_txt,'w')
				print >>ff_ini, '#\tm0d0\tmd0\th0\tz0\telld0\tcd0\trtr0\tmeb0\tmbul0\treb0\tn0\tellb0\tcb0\tmodel\tway'
				print >>ff_ini, '\tmas\tmag\tarcsec\tarcsec\t\t\tarcsec\tmas\tmag\tarcsec\t\t\t\t\t\t'
				ff_ini.close()

			ff_ini = open(file_inimodels_txt, 'a')
			print >>ff_ini, '%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s\t%s' % (number,m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0,Model,way)
			ff_ini.close()
			return k_iter-1,xc,yc,m0d0,h0,99999.,z00,rtr0,xc,yc,meb0,reb0,99999.,n0,cb0,1.,Model,1
		if Model=='exp' or Model=='ser' or Model=='exp+ser':
			constraints.constr(file_constraints,Model,0,FWHM,pix2sec,h0)	# Creating constraints file
		else:
			constraints.constr(file_constraints,Model,1,FWHM,pix2sec,h0)	# Creating constraints file
		#exit()

		status = GALFIT.dec_galfit(find_psf,m0-2.5*log10(EXPTIME),pix2sec,nx,ny,xc,yc,m0d0,magDisk0,h0,z00,elld0,cd0,rmax,meb0,magBul0,reb0,n0,ellb0,cb0,sky_level=0.,PAd=90.,PAb=90.)

		if status==0:
			try:
				print Model
				xc_d,yc_d,m0_d,h,q_d,z0,rtr,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,c_bul,chi2 = res.results(galaxy_name,Model,'0',file_out_txt,file_out_pdf,filter_name,colour_name,colour_value,Aext,z,pix2sec,m0,D,status,tables='tog',gal_number=0,out=1)
			
			except:
				print >>ff, '%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s\t%i' % (k_iter,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,Model,1)
			try:
				print >>ff, '%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s\t%i' % (k_iter,xc_d,yc_d,m0_d,h,q_d,z0,rtr,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,c_bul,chi2,Model,status)
				shutil.move(file_galfit_outimage,'./pics/%i/out_%i.fits' % (number,k_iter))
				shutil.move('subcomps.fits','./pics/%i/sub_%i.fits' % (number,k_iter))
				os.remove('galfit.01')
			except:
				print 'The model crashed!'
				ini_use=='NO'
				chi2=99999.

		else:
			print >>ff, '%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s\t%i' % (k_iter,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,Model,status)
		print >>f_ini, '%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s' % (k_iter,m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0,way)
		if one_dec=='YES' and status==0:
			if status==0:
				return k_iter,xc_d,yc_d,m0_d,h,q_d,z0,rtr,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,c_bul,chi2,Model,status
			else:
				ffff = open(file_out_txt,'a')
				print >>ffff, "%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s\t%i\t%i" % (number,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,99999.,Model,1,0)
				ffff.close()
				exit()

		#print '!!!!!!!!!!!!!!!!!!!!!!!!!',status,k,Model,cod,type(status),type(k),type(Model),type(cod)
		#if k==1: exit()
		#print chi2,cod

		if status!=0 or chi2>2.1:
			ini_use = 'NO'
			way = way + 1
			status = 1
		if (status!=0 and way==4 and k+1<=len(model)) or (status==0 and cod=='1' and k+1<=len(model)):
			k = k + 1
			if k<len(model):	Model = model[k]
			way = 2
			good = 1
		k_iter = k_iter + 1
	ff.close()
	f_ini.close()

	with open('models.txt', 'r') as ff:
		lines = ff.readlines()
		num_lines = len([l for l in lines if l.strip(' \n') != ''])
	n_it = num_lines
	if n_it>1:
		xc_d,yc_d,m0_d,h,q_d,z0,rtr,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,c_bul,chi2 = loadtxt('models.txt', usecols=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], unpack=True, dtype=float)
		Model,status = loadtxt('models.txt', usecols=[16,17], unpack=True, dtype=str)
		numb = loadtxt('models.txt', usecols=[0], unpack=True, dtype=int)
		chi2 = list(chi2)
		kk = chi2.index(min(chi2))

		m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0 = loadtxt('ini.txt', usecols=[1,2,3,4,5,6,7,8,9,10,11,12,13], unpack=True, dtype=float)
		way0 = loadtxt('ini.txt', usecols=[14], unpack=True, dtype=str)
		k_iter = loadtxt('ini.txt', usecols=[0], unpack=True, dtype=int)

		fd = open(file_out_ini,'a')
		print >>fd, '%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s' % (number,m0d0[kk],magDisk0[kk],h0[kk],z00[kk],elld0[kk],cd0[kk],rtr0[kk],meb0[kk],magBul0[kk],reb0[kk],n0[kk],ellb0[kk],cb0[kk],way0[kk])
		fd.close()
		return numb[kk],xc_d[kk],yc_d[kk],m0_d[kk],h[kk],q_d[kk],z0[kk],rtr[kk],xc_bul[kk],yc_bul[kk],me_bul[kk],re_bul[kk],q_bul[kk],n_bul[kk],c_bul[kk],chi2[kk],Model[kk],status[kk]	

	else:
		way0 = way
		fd = open(file_out_ini,'a')
		print >>fd, '%i\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%s' % (number,m0d0,magDisk0,h0,z00,elld0,cd0,rtr0,meb0,magBul0,reb0,n0,ellb0,cb0,way0)
		fd.close()
		return k_iter-1,xc_d,yc_d,m0_d,h,q_d,z0,rtr,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,c_bul,chi2,Model,status







def second_iter(model,file_subcomps,nx,ny,xc,yc,NOISE,pix2sec,m0,EXPTIME,sky_level,file_out_txt,file_out_pdf,filter_name,colour_name,colour_value,Aext,z,D,galaxy_name,find_psf,xc_d,yc_d,m0_d,h,q_d,z0,rtr,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,chi2):

	if model=='exp+ser' or model=='edge+ser':

		if model == 'exp+ser':	MODEL='exp'
		else:	MODEL='edge'

		# A. Subtract bulge from galaxy image => disk	
		iraf.imcopy(file_subcomps+'[3]','bulge.fits')
		
		os.remove(file_subcomps)
		iraf.imarith(operand1=file_gal_clean,op="-",operand2='bulge.fits',result='diskRES.fits')
		try:
			cd1,elld1 = superellipse.super_ellipse('diskRES.fits',xc_d,yc_d,NOISE,1.678*h,m0,pix2sec)
		except:
			if model=='exp+ser':	cd1 = 0.; elld1 = 1.-q_d
			else:	cd1 = -1.;	elld1 = 99999.
	
		
		status = GALFIT.dec_galfit_object(find_psf,'diskRES.fits','disk_fit.fits',m0-2.5*log10(EXPTIME),pix2sec,nx,ny,xc_d,yc_d,m0_d,99999.,h,z0,elld1,cd1,rtr,99999.,99999.,99999.,99999.,99999.,99999.,sky_level=0.,PAd=90.,PAb=99999.)
		os.remove('galfit.01')
		os.remove('subcomps.fits')

		xc_d1,yc_d1,m0_d1,h1,q_d1,z01,rtr1,xc_bul1,yc_bul1,me_bul1,re_bul1,q_bul1,n_bul1,c_bul1,chi21 = res.results(galaxy_name,MODEL,'disk_fit.fits',file_out_txt,file_out_pdf,filter_name,colour_name,colour_value,Aext,z,pix2sec,m0,D,status,tables='tog',gal_number=0,out=1)


		iraf.imcopy('disk_fit.fits'+'[2]','disk.fits')
		iraf.imarith(operand1=file_gal_clean,op="-",operand2='disk.fits',result='bulgeRES.fits')
		try:
			cb2,ellb2 = superellipse.super_ellipse('bulgeRES.fits',xc_bul,yc_bul,NOISE,re_bul,m0,pix2sec)
		except:
			cb2 = 0.;	ellb2 = 1. - q_bul

		status = GALFIT.dec_galfit_object(find_psf,'bulgeRES.fits','bulge_fit.fits',m0-2.5*log10(EXPTIME),pix2sec,nx,ny,xc,yc,99999.,99999.,99999.,99999.,99999.,99999.,99999., me_bul,99999.,re_bul,n_bul,1.-q_bul,cb2,sky_level=0.,PAd=90.,PAb=90.)
		os.remove('galfit.01')
		os.remove('subcomps.fits')
		xc_d2,yc_d2,m0_d2,h2,q_d2,z02,rtr2,xc_bul2,yc_bul2,me_bul2,re_bul2,q_bul2,n_bul2,c_bul2,chi22 = res.results(galaxy_name,'ser','bulge_fit.fits',file_out_txt,file_out_pdf,filter_name,colour_name,colour_value,Aext,z,pix2sec,m0,D,status,tables='tog',gal_number=0,out=1)


		

		status = GALFIT.dec_galfit(find_psf,m0-2.5*log10(EXPTIME),pix2sec,nx,ny,xc,yc,m0_d1,99999.,h1,z01,elld1,cd1,rtr,me_bul2,99999.,re_bul2,n_bul2,ellb2,cb2,sky_level=0.,PAd=90.,PAb=90.)
		xc_d,yc_d,m0_d,h,q_d,z0,rtr,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,c_bul,chi2 = res.results(galaxy_name,model,'0',file_out_txt,file_out_pdf,filter_name,colour_name,colour_value,Aext,z,pix2sec,m0,D,status,tables='tog',gal_number=0,out=1)
		os.remove('galfit.01')

		#shutil.move(file_galfit_outimage,'./pics/%i/out_%i.fits' % (number,k_iter))
		#shutil.move('subcomps.fits','./pics/%i/subcomps.fits' % (number))

		return xc_d,yc_d,m0_d,h,q_d,z0,rtr,xc_bul,yc_bul,me_bul,re_bul,q_bul,n_bul,c_bul,chi2,status

	


	






		

	
	  
	
