"""Library equivalent (pending-ci): the same reduction with astropy CCDData + ccdproc, compared with calibrate.py.

pip install -r ../requirements.txt   (astropy 8.0.2, ccdproc 2.5.1, astroscrappy 1.3.0)
python calibrate_ccdproc.py
"""
import astropy.units as u
import ccdproc
import numpy as np
from astropy.nddata import CCDData

import calibrate
import camera


def to_ccd(arr):
    return [CCDData(a, unit="adu") for a in arr]


def reduce(seed=13):
    f = camera.frames(seed)
    clip = dict(method="average", sigma_clip=True, sigma_clip_low_thresh=3, sigma_clip_high_thresh=3,
                sigma_clip_func=np.ma.median, sigma_clip_dev_func=ccdproc.combiner.mad_std)
    bias = ccdproc.combine(to_ccd(f["bias"]), **clip)
    dark = ccdproc.combine([ccdproc.subtract_bias(c, bias) for c in to_ccd(f["dark"])], **clip)
    flat = ccdproc.combine([ccdproc.subtract_bias(c, bias) for c in to_ccd(f["flat"])], **clip)
    flux = []
    for i, light in enumerate(to_ccd(f["light"])):
        sci = ccdproc.subtract_dark(ccdproc.subtract_bias(light, bias), dark, exposure_time=camera.EXPTIME * u.s,
                                    exposure_unit=u.s, scale=False)
        sci = ccdproc.flat_correct(sci, flat, norm_value=np.median(flat.data))
        sci = ccdproc.cosmicray_lacosmic(sci, gain=camera.GAIN * u.electron / u.adu, readnoise=camera.READ_E,
                                         sigclip=6.0)
        flux.append(calibrate.photometry(np.asarray(sci.data), camera.star_x(i), camera.Y_STAR)[0])
    rel = np.array(flux) / np.median(flux)
    return rel, round(100 * float(rel.std()), 3)


if __name__ == "__main__":
    rel, rms = reduce()
    print(f"ccdproc light curve rms {rms}% (numpy solution: 0.389%)")
