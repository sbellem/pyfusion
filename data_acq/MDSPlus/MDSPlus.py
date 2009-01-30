"""  Module implemented by a choice of two dodgy modules
Choice is MDSmod='MDSplus' or 'pmds'
pmds: OK, but hard to find new version, hard to compile on W32 
     Advantage: thin client, so works on any MDSIP server
     Disavantage: Speed may be reduced because of client-server arch
MDSplus: Is a superseded embryonic object implementation by Tom Fredian
     Advantage: Should be faster, links to standard MDSplus distro.
     In principle should be able to do thin client, but I didn't test it.


"""

import pyfusion
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from numpy import array, searchsorted


def _loadmds_pmds(mdsch, shot):
    from mdsutils import pmds
    pmds.mdsconnect(mdsch.mds_server)
    pmds.mdsopen(mdsch.mds_tree, int(shot))
    data = array(pmds.mdsvalue(mdsch.mds_path))
    dim_data = array(pmds.mdsvalue('dim_of(' + mdsch.mds_path+')'))
    pmds.mdsclose(mdsch.mds_tree, shot)
    pmds.mdsdisconnect()
    return [dim_data, data]
            
def _loadmds_MDSplus(mdsch, shot):
    import MDSplus as M
    # at present, only access local data through the dynamic library 
    print('W: module MDSplus accessing local MDS server only, request was %s ' % 
          mdsch.mds_server)
    M.TreeOpen(mdsch.mds_tree, int(shot))
# This is an early version of the MDSplus pbject interface to python. There
# is a much newer nicer version.  One day I will code it in to avoid the 
# kludges.
# In this implementation, specifying time bounds is used to force the TDI
# interpreter to use a different evaluation path to avoid a bug, and
# can provide a big speed up if the data interval is a small part of
# the total interval: 
# note: For dtacq shots in 58100 range, need delta>=30us, because less data
#     is returned than expected (another bug?)
    delta=1e-4
    bounds=str("[%f:%f]") % (pyfusion.settings.SHOT_T_MIN, 
                             pyfusion.settings.SHOT_T_MAX+delta)
    print mdsch.mds_path+bounds
    sig = M.TdiExecute(mdsch.mds_path+bounds)
    if pyfusion.settings.VERBOSE>4: print sig
    data = sig.data()
    if pyfusion.settings.VERBOSE>10: 
        import pylab as pl
        pl.plot(sig.data())
        pl.title('mdsch.mds_path+bounds')
        pl.show()
    sigdim = M.TdiExecute('dim_of(' + mdsch.mds_path+bounds+')')
    dim_data = sigdim.data()
    if len(dim_data)==1:  # ne_centre has this problem - try another tack
        print(' using kludge #2'),
        sig = M.TdiExecute('1.*'+mdsch.mds_path)
        data=sig.data()
        sigdim = M.TdiExecute('dim_of('+mdsch.mds_path+')')
        dim_data=sigdim.data()
        print('retrieved data lenght %d, timebase length %d' %
              (len(data), len(dim_data)))
    M.TreeClose(mdsch.mds_tree, int(shot))
    return [dim_data, data]

def _loadmds_MDSplus_dev(mdsch, shot):
    import MDSplus as M
    mdstree = M.Tree(mdsch.mds_tree, int(shot))
    mdsnode = mdstree.getNode(mdsch.mds_path)
    mdsnode.getData()
    data = mdsnode.data()
    raise NotImplementedError, "Can't figure out how to get dim_of..."
    
MDSPLUS_PYTHON_MODULE_DICT = {
    'pmds':_loadmds_pmds,
    'MDSPlus':_loadmds_MDSplus,
    'MDSPlus_dev':_loadmds_MDSplus_dev
    }

def _loadmds(mdsch,shot, invert=False):
    MDSmod=pyfusion.settings.MDSPLUS_PYTHON_MODULE
    mds_func = MDSPLUS_PYTHON_MODULE_DICT[MDSmod]

    # this try/except covers too much - need to break it up
    if pyfusion.settings.VERBOSE>4:
        [dim_data, data] = mds_func(mdsch, shot)
    else:
        try:
            [dim_data, data] = mds_func(mdsch, shot)
        except:
        # using the jScope/mdsdcl convention for "full path" here - hope it is right!
        #  mirnov_dtacq ideally should be preceded by a : 
        # (dgp: mirnov_dtacq is H-1 specific - any mirnov_dtacq customisations would go in devices/H1)
            msg=str(('Error accessing server %s: Shot %d, \\%s::top%s') % 
                    (mdsch.mds_server, shot, mdsch.mds_tree, mdsch.mds_path))
            print(msg)
            raise LookupError, msg

    if invert:
        data = -data
    return [dim_data,data]

class ProcessData:
    def load_channel(self, mdsch, shot, invert=False):        
        [dim_data,data] = _loadmds(mdsch,shot,invert=invert)
        t_lim = searchsorted(dim_data,[pyfusion.settings.SHOT_T_MIN, pyfusion.settings.SHOT_T_MAX])
        if pyfusion.settings.VERBOSE>4: 
            print('choosing data indices %d to %d') % (t_lim[0],t_lim[1])
        output_MCT = pyfusion.MultiChannelTimeseries(dim_data[t_lim[0]:t_lim[1]])
        output_MCT.add_channel(data[t_lim[0]:t_lim[1]], mdsch.name)
        return output_MCT

class MDSPlusChannel(pyfusion.Channel):
    __tablename__ = 'mdspluschannels'
    __mapper_args__ = {'polymorphic_identity':'MDSPlus'}
    id = Column('id', Integer, ForeignKey('channels.id'), primary_key=True)
    mds_server = Column('mds_server', String(50))
    mds_tree = Column('mds_tree', String(50))
    mds_path = Column('mds_path', String(50))
    time_unit_in_seconds = Column('time_unit_in_seconds', Float, default = 1)
