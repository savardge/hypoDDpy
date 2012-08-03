# hypoDDpy

This a collection of tools to run [HypoDD](http://www.ldeo.columbia.edu/~felixw/hypoDD.html) by Felix Waldhauser.

![Flowchart 1](https://raw.github.com/krischer/hypoDDpy/master/img/flowchart.png)

### Installation
hypoDDpy is currently working with HypoDD 2.1b which you have to acquire from Felix Waldhauser.

Put the archive in the following subdirectory:
> hypoddpy/src/HYPODD\_2.1b.tar.gz

The src directory will likely not exists.

Then run *either of the* following two command, depending on which Python module installer you prefer.

> pip install -v -e .
> python setup.py develop

The inplace install is a good idea because there is a chance that you will have to adjust the source code.


### Running it

It is steered via a Python script that you will have to create. It should be rather self explanatory.

After you created it, simply run it to perform the relocation.

```python
import glob
from hypoddpy import HypoDDRelocator


# Init the relocator with the working directory and some necessary
# configuration values.
#
# The working dir is where all the working files and some output files will be
# stored.
# All the other attributes are related to the cross correlation and should be
# self-explanatory.
relocator = HypoDDRelocator(working_dir="relocator_working_dir",
    cc_time_before=0.05,
    cc_time_after=0.2,
    cc_maxlag=0.1,
    cc_filter_min_freq=1.0,
    cc_filter_max_freq=20.0,
    cc_p_phase_weighting={"Z": 1.0},
    cc_s_phase_weighting={"Z": 1.0, "E": 1.0, "N": 1.0},
    cc_min_allowed_cross_corr_coeff=0.4)

# Add the necessary files. Call a function multiple times if necessary.
relocator.add_event_files(glob.glob("events/*.xml"))
relocator.add_waveform_files(glob.glob("waveform/*.mseed"))
relocator.add_station_files(glob.glob("station/*.xml"))

# Setup the velocity model. This is just a contant velocity model.
relocator.setup_velocity_model(\
    model_type="layered_p_velocity_with_constant_vp_vs_ratio",
    layer_tops=[(-10000, 5.8)],
    vp_vs_ratio=1.73)

# Start the relocation with the desired output file.
relocator.start_relocation(output_event_file="relocated_events.xml")
```
