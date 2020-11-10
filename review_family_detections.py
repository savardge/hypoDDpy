from obspy import read_inventory, read, read_events, Catalog
from pyrocko import obspy_compat
from pyrocko.model.event import Event as pyEvent
from pyrocko.gui.marker import EventMarker, PhaseMarker
from eqcorrscan.core.match_filter import Party, Tribe, Template
from pyrocko.util import str_to_time
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")
Logger = logging.getLogger(__name__)

obspy_compat.plant()
from glob import glob
import os
import shutil

# Station info
inv = read_inventory("/media/genevieve/SanDisk_2TB/cami/station_locations_info/station_X1_to_X11.xml")
inv += read_inventory("/media/genevieve/SanDisk_2TB/frs_borehole/downhole_geodes_ZNE.xml")

file = sys.argv[1]
print(file)

# Waveforms
stream = read(file)
detection_id = file.replace(".mseed", "")

# Event info

dum = file.split("_")[-1]
family_file_root = file.replace("_%s" % dum, "")
family_file = glob("family_%s_ndet*.tgz" % family_file_root)
if not family_file:
    Logger.error("No family file found.")
party = Party().read(family_file[0])
family = party[0]
template = family.template
event = template.event

picks_auto = []
for p in event.picks:
    nscl = (p.waveform_id.network_code, p.waveform_id.station_code,
            p.waveform_id.location_code, p.waveform_id.channel_code)
    kind = 1 if p.phase_hint == "P" else 2
    pick_time = str_to_time(p.time.strftime("%Y-%m-%d %H:%M:") + "%f" % (p.time.second + p.time.microsecond * 1e-6))

    m = PhaseMarker(nslc_ids=[nscl], tmin=pick_time, tmax=pick_time, kind=kind, phasename=p.phase_hint)
    picks_auto.append(m)

return_tag, markers_out = stream.snuffle(inventory=inv, markers=picks_auto, ntracks=8)
