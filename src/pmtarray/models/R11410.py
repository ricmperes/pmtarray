from pmtarray.unit import PMTunit

class R11410(PMTunit):
    """Class of the R11410 3" PMT. The current standard photosensor in DM experiments.
    Ref: https://arxiv.org/pdf/2104.15051.pdf and internal Hamamatsu documentation.
    """
    def __init__(self):
        self.name = 'R11410, 3" PMT by Hamamatsu'
        self.type = 'circular'
        self.diameter_packaging = 76 # mm
        self.active_diameter = 64 # mm
        self.diameter_tolerance = 2.6
        self.qe = 0.34
        self.active_area_correction = 1.

        self.set_dependant_properties()