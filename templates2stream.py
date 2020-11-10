from eqcorrscan.core.match_filter import Tribe
from obspy import Catalog
import os
from glob import glob
from obspy import Stream, read
import sys
from obspy.taup.taup_geo import calc_dist
from obspy.geodetics.base import degrees2kilometers
from obspy.geodetics.base import gps2dist_azimuth
from obspy import read_inventory, Inventory

inv = Inventory()
for f in glob("/home/genevieve.savard/hypoDDpy/station_files/*.xml"):
    inv += read_inventory(f)
    
    
def plot_3cols(stream, event):
    stations = list(set([tr.stats.station for tr in stream]))
    nsta = len(stations)
    
    plt.rcParams['figure.figsize'] = [15, 15]
    fig, axs = plt.subplots(nsta, 3, sharex=True, figsize=(24, nsta*5))
    
    for i, sta in enumerate(stations):
        
        trn = stream.select(station=sta, channel="DPN")[0]
        tre = stream.select(station=sta, channel="DPE")[0]
        trz = stream.select(station=sta, channel="DPZ")[0]
        
        tplt = trn.times("matplotlib")
        axs[i][0].plot_date(tplt, trn.data, "k")
        axs[i][0].set_title(trn.id)
        axs[i][1].plot_date(tplt, tre.data, "k")
        axs[i][1].set_title(tre.id)
        axs[i][2].plot_date(tplt, trz.data, "k")
        axs[i][2].set_title(trz.id)
    plt.suptitle("%s, depth = %f, depth_error = %f" % (event.origins[0].time, event.origins[0].depth, event.origins[0].depth_errors["uncertainty"]))
    plt.show()
    
    
def get_stream_hour(tmin, tmax, stations):
    WF_DIR_ROOT_500Hz = "/home/gilbert_lab/cami_frs/borehole_data/sac_daily_nez_500Hz"
    WF_DIR_ROOT_HAWK = "/home/gilbert_lab/cami_frs/hawk_data/sac_data_mps/"

    detst = Stream()
    for station in stations:
        pattern = os.path.join(WF_DIR_ROOT_500Hz, tmin.strftime("%Y%m%d"), "*%s*DP*" % station)
        if glob(pattern):
            detst += read(pattern, starttime=tmin, endtime=tmax)
        pattern_hawk = os.path.join(WF_DIR_ROOT_HAWK, "X7*", station, "*DP*.D.%s*" % tmin.strftime("%Y%m%d"))
        if glob(pattern_hawk):
            detst += read(pattern_hawk, starttime=tmin, endtime=tmax)
    
    # Remove channels with DP1, DP2 (only keep DPN, DPE)
    for tr in detst:
        if tr.stats.channel in ["DP1", "DP2"]:
            detst.remove(tr)
            
    # Convert to nm/s
    m2nm = 1e9
    for tr in detst:
        tr.data = tr.data * m2nm
        #tr.stats.network = "XX"
    detst.detrend("demean")
    
    #detst.resample(SAMPLING_RATE)

    return detst

templist = [sys.argv[1]]
#templist = glob("/home/gilbert_lab/cami_frs/eqcorrscan/templates_both_f60/templates/*.tgz")
for f in templist:
#     if "tribe" in f:
#         continue
#     print(f)
#     tribe = Tribe().read(f)
#     template = tribe[0]
#     name = template.name
#     stream_fname = os.path.join("templates", "waveforms", "%s.mseed" % name)
#     if os.path.exists(stream_fname):
#         continue
#     event = template.event
#     print(event.origins[0])
#     origt = event.origins[0].time
#     print(origt)
#     tmin = origt - 2.0
#     tmax = origt + 6.0
#     stations = list(set([p.waveform_id.station_code for p in event.picks]))
#     print(stations)
#     stream = get_stream_hour(tmin, tmax, stations)
    
#     stream.write(stream_fname, format="MSEED")
    
#     if event.origins[0].depth < 50:
#         stream.write(os.path.join("templates_less50m", "%s.mseed" % name), format="MSEED")
        
    for f in templist:
        if "tribe" in f:
            continue
        print(f)
        tribe = Tribe().read(f)
        template = tribe[0]
        event = template.event
        depth = event.origins[0].depth
        if depth < 10:
            origt = event.origins[0].time
            evlat = event.origins[0].latitude
            evlon = event.origins[0].longitude

            tmin = origt - 0.5
            tmax = origt + 5.0
            name = template.name
            fname = os.path.join("templates", "waveforms", "%s.mseed" % name)
            stream = read(fname)
            for tr in stream:
                station = tr.stats.station
                coords = inv.get_coordinates(tr.id, origt)
                stalat = coords["latitude"] 
                stalon = coords["longitude"] 
    #             distdeg = calc_dist(evlat, evlon, stalat, stalon, 6378.1)
    #             distkm = degrees2kilometers(distdeg)
                dist = gps2dist_azimuth(evlat, evlon, stalat, stalon)[0]
                tr.stats.distance = dist

            stream.sort()
            #stream.traces.sort(key=lambda x: x.stats.distance)
            stream.trim(starttime=tmin, endtime=tmax).filter("lowpass", freq=60)
            plot_3cols(stream, event)
            plt.savefig(os.path.join("templates", "waveforms", "%s.png" % name), dpi=300)