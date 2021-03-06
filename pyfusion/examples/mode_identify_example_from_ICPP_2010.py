import pylab as pl

from numpy import intersect1d

# manually enter the mean and sd for three modes, called by color
# n=1
blue = [1.020, 1.488, 1.348, -0.080, 0.989]
bluesd= [0.077, 0.016, 0.048, 0.020, 0.008 ]
# n=0
lblue =[-1.146, -1.094, 0.608, 0.880, 0.164]
lbluesd=[ 0.048, 0.033, 0.034, 0.033, 0.042]
# n=2
red =[2.902, 2.217, 2.823, 1.021, 2.157]
redsd= [0.023, 0.006, 0.028, 0.025, 0.007 ]

sd = []
sdlb = []
sdred = []

sh = []
amp = []
ind = []
#arr=loadtxt('MP_27233_cf_syama.txt',skiprows=4)
# read in the delta phases from the aggregated pyfusion database
# and build up a list of flucstrucs and the sum of squares relative to the
# three modes.
arr=loadtxt('MP512all.txt',skiprows=4)
for i,rw in enumerate(arr):
    sh.append(int(rw[0]))
    sd.append(sum((rw[8:]-blue)**2))
    sdlb.append(sum((rw[8:]-lblue)**2))
    sdred.append(sum((rw[8:]-red)**2))
    amp.append(rw[4])
    ind.append(i)

#run -i ../../plot_text_pyfusion.py filename='MP_27233_cf_syama.txt' skip=4
run -i ../../plot_text_pyfusion.py filename='MP512all.txt' skip=4

# find the indices of modes within a  short distance from the classification
neq0 = (array(sdlb) < 1).nonzero()[0]
neq1 = (array(sd) < 1).nonzero()[0]
neq2 = (array(sdred) < 1).nonzero()[0]

# do a crude plout by color=mode only
msize=40
pl.scatter(ds['t_mid'][neq1],ds['freq'][neq1],hold=0,s=msize)
pl.scatter(ds['t_mid'][neq0],ds['freq'][neq0],c='cyan',s=msize)
pl.scatter(ds['t_mid'][neq2],ds['freq'][neq2],c='red',s=msize)

# now read in HB database into arrays of ne, beta indexed by shot
arr=loadtxt("../../../datamining/LHD_iss_DB07_data_only_selected.csv", skiprows=1,delimiter=',',usecols=[0,1,2,3,4,5,6,7,10,17,18,19])

#test purposes - actuallyneed beta, ne in shot array
neq0 = (array(sdlb) < 1).nonzero()[0]
neq1 = (array(sd) < 1).nonzero()[0]
neq2 = (array(sdred) < 1).nonzero()[0]


beta=arr[:,10]
print ('max beta found is %.2g' % max(beta))

ne=arr[:,7]

shot=arr[:,0]
bet=zeros(60000)
ne=zeros(60000)
shot=arr[:,0]
for i,s in enumerate(shot): 
    bet[s]=arr[i,11]

for i,s in enumerate(shot): 
    ne[s]=arr[i,8]

# We are now ready to plot all neq2 (or 1 etc) shots coded by density or beta

"""
pl.clf()  # gets rid of extra colorbar
rc('font', **{'size':18})
pl.gcf().subplots_adjust(left=0.08, right=1, bottom=0.09, top=0.92)
sind=neq2
#pl.scatter(ds['t_mid'][sind], freq_scale*ds['freq'][sind],dot_size*np.log(ds['amp'][sind]/amp_scale),ds['a12'][sind],hold=0)
pl.scatter(ds['t_mid'][sind], freq_scale*ds['freq'][sind],dot_size*np.log(ds['amp'][sind]/amp_scale),ne[ds['shot'][sind]],hold=0)

colorbar()
pl.gcf().subplots_adjust(left=0.08, right=0.80, bottom=0.09, top=0.92)

pl.ylabel('Frequency (kHz)') ; pl.xlabel('time (S)'); pl.title('N=2 modes, by density HP database DB07_25')

"""


hbshots = [46357,46365,46370,47576,47577,47644,47648,47650,47725]
# These are alternatives for selecting for mode (first example), mode and the high beta subgroup

######################################3
# mode and a hb shot
sind=[]
for sh in hbshots:
    shot_hits = (ds['shot'] == sh).nonzero()[0]
    neq1_hits = (array(sdred) < 1).nonzero()[0]
    hits = intersect1d(shot_hits, neq1_hits)
    print("%d, " % (len(shot_hits))),
    if len(hits)>0: sind.extend(hits)

neq2_highbeta=sind
#neq1_highbeta=sind
#neq0_highbeta=sind

"""
"""
# These appear to be two failed attempts to find fluxstrucs for shots
# in a subrange with particular modes
sind=[]
for sh in shots:
    hits=((ds['shot'] == sh) and (array(sdred) < 1)).nonzero()[0]
    if len(hits)>0: sind.extend(hits)


sind=[]
for sh in shots:
    hits=array((ds['shot'] == sh).tolist() and (array(sdred) < 1).tolist()).nonzero()[0]
    if len(hits)>0: sind.extend(hits)


"""


