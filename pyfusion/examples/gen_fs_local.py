""" test generation of flucstrucs.
#exception=None catches no exceptions, so you get a stop and a traceback
#exception=Exception catches all, so it continues, but no traceback
python dm/gen_fs.py shot_range=[27233] exception=None

71 secs to sqlite.txt (9MB) (21.2k in basedata, 3.5k fs, 17.7k float_delta
34 secs with db, but no fs_set.save()
17 secs to text 86kB - but only 1k fs
Apr 2013 - checked timing - deepcopy was slowing it down. 32/41 54185 prepfs.py
"""
import subprocess, sys, warnings
from numpy import sqrt, mean, argsort, average, random
import pyfusion
from pyfusion.debug_ import debug_
import sys
from time import sleep, time as seconds
import os

def timeinfo(message):
    if show_times == 0: return
    global st, st_0
    try:
        dt = seconds()-st
    except:
        print('Time:' + message + '(first call)')
        st = seconds()
        st_0 = seconds()
        return
    print("Time: {m} in {dt:.2f}/{t:.2f}".format(m=message, dt=dt, t=seconds()-st_0))
    st = seconds()
    return
    

_var_default="""
lhd = pyfusion.getDevice('LHD')

#min_shot = 84000
#max_shot = 94000
#every_nth = 10

#shot_range = range(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

debug=0
show_times=1
shot_range = [27233]
#shot_range = range(90090, 90110)
n_samples = 512
overlap=1.0
diag_name= 'MP'
exception=Exception
time_range = None
min_svs=1
max_H=0.97
info=2
separate=1
method='rms'


# ids are usually handled by sqlalchemy, without SQL we need to look after them ourselves
fs_id = 0
"""
exec(_var_default)

# ideally should be a direct call, passing the local dictionary
import pyfusion.utils
exec(pyfusion.utils.process_cmd_line_args())

count = 0  #  we print the header right before the first data

for shot in shot_range:
    while(os.path.exists(pyfusion.root_dir+'/pause')):
        print('paused until '+ pyfusion.root_dir+'/pause'+ ' is removed')
        sleep(int(20*(1+random.uniform())))  # wait 20-40 secs, so they don't all start together

    timeinfo('start shot {s}'.format(s=shot))
    try:
        d = lhd.acq.getdata(shot, diag_name)
        timeinfo('data read')
        if time_range != None:
            d.reduce_time(time_range, copy=False)
        sections = d.segment(n_samples, overlap)
        print(d.history, len(sections), pyfusion.version.get_version('verbose'))
        try:
            for k in pyfusion.conf.history.keys():
                print(pyfusion.conf.history[k][0].split('"')[1])
                if info>1: sys.stdout.writelines(pyfusion.conf.utils.dump())
        except: pass    

        ord_segs = []
        for ii,t_seg in enumerate(sections):
            ord_segs.append(t_seg)
        ord = argsort([average(t_seg.timebase) for t_seg in ord_segs])
        timeinfo('beginning flucstruc loop')
        for idx in ord:
            t_seg = ord_segs[idx]
            fs_set = t_seg.flucstruc(method=method, separate=separate)
            for fs in fs_set:
                if count==0: 
                    # show history if info says to, and avoid starting line with a digit
                    if info > 0: print('< '+fs.history.replace('\n201','\n< 201'))
                    print('Shot    time      SVS    freq  Amp    a12   p    H        Phases')
                count += 1
                if fs.H < max_H and fs.p>0.01 and len(fs.svs())>min_svs:
                    phases = ' '.join(["%5.2f" % j.delta for j in fs.dphase])
                    # was t_seg.scales, but now it is copies, t_seg is not updated 
                    RMS_scale = sqrt(mean(fs.scales**2)) 
                    adjE = fs.p*fs.E*RMS_scale**2
                    debug_(debug)
                    if pyfusion.orm_manager.IS_ACTIVE: 
                    # 2-2.05, MP: 11 secs, 87  , commit=False 10.6 secs 87
                    # commits don't seem to reduce time.    
                        fs.save(commit=True)           
                    else: 
                        # 20121206 - time as %8.5g (was 7.4) 
                        # caused apparent duplicate times
                        print ("%d %8.5g %s %6.3g %6.3f %.2f %.3f %.3f    %s" % (
                                shot, fs.t0, "{0:8b}".format(fs._binary_svs), 
                                fs.freq/1000., sqrt(fs.E*fs.p)*RMS_scale, 
                                fs.a12, fs.p, fs.H, phases))

        # the -f stops the rm cmd going to the terminal
#        subprocess.call(['/bin/rm -f /data/tmpboyd/pyfusion/FMD*%d*' %shot], shell=True)
#        subprocess.call(['/bin/rm -f /data/tmpboyd/pyfusion/SX8*%d*' %shot], shell=True)
    except exception:
#set Exception=None to allow traceback to show - it can never happen
# otherwise, the warnigns.warn will prevent multiple identical messages
        warning_msg = str('shot %d not processed: %s' % 
                          (shot,sys.exc_info()[1].__repr__()))
        warnings.warn(warning_msg,stacklevel=2)

if pyfusion.orm_manager.IS_ACTIVE: 

    pyfusion.orm_manager.Session().commit()
    pyfusion.orm_manager.Session().close_all()

timeinfo('finished')
