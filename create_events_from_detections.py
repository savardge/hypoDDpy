from obspy import read_inventory, Catalog
from obspy.core.event import Pick, Event
from eqcorrscan.core.match_filter import Party
import sys
import os
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s")
Logger = logging.getLogger(__name__)

# Station info
inv = read_inventory("station_files/downhole_geodes_ZNE.xml")
inv += read_inventory("station_files/station_X1_to_X11.xml")

# Family to process
family_file = sys.argv[1]
family_folder = os.path.split(family_file)[0]
family_name = os.path.split(family_file)[1]
Logger.info("Processing family with path name: %s" % family_file)
Logger.info("Family name: %s" % family_name)
party = Party().read(family_file)
family = party[0]
ndets = len(family.detections)
if ndets == 0:
    Logger.error("No detections for this family.... weird")

# Template info
template = family.template
prepick = template.prepick
template_event = template.event
min_template_starttime = min([tr.stats.starttime for tr in template.st])

catalog = Catalog()
for i, detection in enumerate(family.detections):
    Logger.info("Working on detection %d/%d with ID %s" % (i+1, ndets, detection.id))
    detect_time = detection.detect_time

    # Make picks for detections from template picks
    det_picks = []
    for p in template_event.picks:
        delay_template = p.time - min_template_starttime
        det_pick_time = detect_time + delay_template
        pick = Pick(time=det_pick_time, phase_hint=p.phase_hint, waveform_id=p.waveform_id)
        det_picks.append(pick)

    # figure out origin time for detection
    pick1_temp = template_event.picks[0]
    origin_det = template_event.origins[0].copy()
    pick1_det = [p for p in det_picks if p.waveform_id == pick1_temp.waveform_id][0]
    origin_det.time = pick1_det.time - (pick1_temp.time - template_event.origins[0].time)

    # Create and save event for detection
    event = Event(picks=det_picks, origins=[origin_det])
    event.preferred_origin_id = event.origins[0].resource_id
    catalog.append(event)

catalog_dir = os.path.join(os.getcwd(), "families_events")
catalog_fname = "catalog_" + family_name.split(".")[0] + ".xml"
catalog_file = os.path.join(catalog_dir, catalog_fname)
Logger.info("Now writing catalogue to file %s" % catalog_file)
catalog.write(catalog_file, format="QUAKEML")
