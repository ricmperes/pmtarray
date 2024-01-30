from pmtarray.unit import PMTunit

class R12699(PMTunit):
    """Class of the R11410 3" PMT. The current standard photosensor in DM experiments.
    Ref: internal Hamamatsu documentation.
    """
    def __init__(self):
        self.name = 'R12699, 2" square PMT by Hamamatsu'
        self.type = 'square'
        self.width = self.width_package = 56
        self.height = self.height_package = 56
        self.width_tolerance = 0.3
        self.height_tolerance = 0.3
        self.width_active = 48.5
        self.height_active = 48.5
        self.active_area_correction = 1.
        self.D_corner_x_active = ((self.width_package - 
                                    self.width_active)/2 + 
                                    self.width_tolerance)
        self.D_corner_y_active = ((self.height_package - 
                                    self.height_active)/2 + 
                                    self.height_tolerance)
        self.qe = 0.33
        self.set_dependant_properties()