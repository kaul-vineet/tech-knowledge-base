"""Library equivalent (pending-ci, needs network): the same cone as ADQL against a public TAP service with pyvo.

pip install -r ../requirements.txt   (pyvo 1.9.1)        python pyvo_query.py
Gaia data are CC BY-NC 3.0 IGO (ESA); cite and credit 'ESA/Gaia/DPAC' if you use the rows (lesson 21).
"""
import pyvo

import catalog

GAIA_TAP = "https://gea.esac.esa.int/tap-server/tap"


def gaia_cone(ra=83.82, dec=-5.39, radius=0.05):
    service = pyvo.dal.TAPService(GAIA_TAP)
    return service.run_sync(catalog.adql_cone(ra, dec, radius)).to_table()


if __name__ == "__main__":
    table = gaia_cone()
    print(len(table), "Gaia DR3 sources within 0.05 deg of (83.82, -5.39)")
