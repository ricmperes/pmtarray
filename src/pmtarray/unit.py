from importlib import import_module
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle


class PMTunit():
    """Class to represent a PMT unit."""

    def __init__(self, model):
        self.get_model_file(model)
        self.get_model_geometry()
        self.set_dependant_properties()

    def get_model_file(self, model):
        """Fetch the PMT model from the model library."""
        
        from pmtarray.models import model_lib
        if model in model_lib.keys():
            self.model = model_lib[model]
        else:
            raise ValueError('Model not found. Please make a PR to add it.')
        
    def get_model_geometry(self):
        """Loads model geometric properties from the model file.

        Raises:
            ModuleNotFoundError: raised if the model file is not found.
        """
        try:
            model_module = import_module(f'pmtarray.models.{self.model}')
            model_class = getattr(model_module, self.model)
            _model = model_class()

            self.name = _model.name
            self.type = _model.type

            if self.type == 'circular':
                self.diameter_packaging = _model.diameter_packaging
                self.active_diameter = _model.active_diameter
                self.diameter_tolerance = _model.diameter_tolerance
                self.active_area_correction = _model.active_area_correction

            elif self.type == 'square':
                self.width = self.width_package = _model.width_package
                self.height = self.height_package = _model.height_package
                self.width_active = _model.width_active
                self.height_active = _model.height_active
                self.width_tolerance = _model.width_tolerance
                self.height_tolerance = _model.height_tolerance
                self.D_corner_x_active = _model.D_corner_x_active
                self.D_corner_y_active = _model.D_corner_y_active
                self.active_area_correction = _model.active_area_correction

            else:
                raise ValueError('Model type not recognized.')

            self.qe = _model.qe
            self.set_dependant_properties()

        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                'Model not found. Please make a PR to add it.')
    
    def set_dependant_properties(self):
        """Defines dependant properties of the PMT units: total area, active
        area and active area fraction.
        """
        if self.type == 'square':
            self.width_unit = self.width + 2*self.width_tolerance
            self.height_unit = self.height + 2*self.height_tolerance
            self.total_area = self.width_unit*self.height_unit
            self.active_area = (self.width_active *
                                self.height_active *
                                self.active_area_correction)
            
        elif self.type == 'circular':
            self.radius = (self.diameter_packaging)/2
            self.active_radius = self.active_diameter/2
            self.total_area = np.pi*self.radius**2
            self.active_area = np.pi*self.active_radius**2 * self.active_area_correction
        else:
            raise ValueError('Model type not recognized.')
        self.active_area_fraction = self.active_area/self.total_area

            
    def get_unit_centre(self)->Tuple[float, float]:
        """Get the centre of the PMT unit

        Returns:
            tuple: (x,y) of the centre of the PMT unit in PMT unit 
                coordinates.
        """
        if self.type == 'circular':
            return (0,0)
        elif self.type == 'square':
            return (self.width_unit/2, self.height_unit/2)
        else:
            raise ValueError('Model type not recognized.')
    
    def get_unit_active_centre(self)->Tuple[float, float]:
        """Get the centre of the active area of the PMT unit

        Returns:
            tuple: (x,y) of the centre of the active area of the PMT unit 
                in PMT unit coordinates.
        """
        if self.type == 'circular':
            return (0,0)
        elif self.type == 'square':

            x = self.D_corner_x_active + self.width_active/2
            y = self.D_corner_y_active + self.height_active/2
            return (x,y)    
        else:
            raise ValueError('Model type not recognized.')
    
    def plot_model(self, xy = (0,0), figax = None):
        """Make a plot of the PMT unit model

        Args:
            xy (tuple, optional): coordinates of the bottom left corner. 
                Defaults to (0,0).
            figax (_type_, optional): figure and axis environment. 
                Defaults to None.

        Returns:
            _type_: updated figure and axis environment
        """
        if self.type == 'circular':
            return self.plot_round_model(xy, figax)
        elif self.type == 'square':
            return self.plot_square_model(xy, figax)
        else:
            raise ValueError('Model type not recognized.')
        
    def plot_square_model(self, xy = (0,0), figax = None):
        """Make a plot of the PMT unit model

        Args:
            xy (tuple, optional): coordinates of the bottom left corner. 
                Defaults to (0,0).
            figax (_type_, optional): figure and axis environment. 
                Defaults to None.

        Returns:
            _type_: updated figure and axis environment
        """
        if self.type != 'square':
            raise ValueError('This plotting function is for type square PMTs.')
        if figax == None:
            fig, ax = plt.subplots(1,1,figsize = (5,5))
        ax.add_patch(Rectangle((xy[0]+self.width_tolerance, 
                                xy[1]+self.height_tolerance), 
                   width=self.width,
                   height=self.height,
                   facecolor = 'gray',
                   alpha = 0.3, edgecolor = 'k',
                   label = 'Packaging area', zorder = 1))
        ax.add_patch(Rectangle((xy[0]+self.D_corner_x_active,
                                xy[1]+self.D_corner_y_active), 
                               width=self.width_active, 
                               height=self.height_active, 
                               facecolor = 'k', alpha = 0.8, edgecolor = 'k',
                              label = 'Active area', zorder = 2))
        
        geometric_centre = self.get_unit_centre()
        active_centre = self.get_unit_active_centre()

        ax.plot(geometric_centre[0], geometric_centre[1], 'o', 
                c = 'g', label = 'Geometric centre')
        ax.plot(active_centre[0], active_centre[1], 'x',
                c = 'r', label = 'Active centre')
        
        ax.set_xlim(xy[0]-0.1*self.width_unit, xy[0]+1.1*self.width_unit)
        ax.set_ylim(xy[1]-0.1*self.height_unit, xy[1]+1.1*self.height_unit)
        ax.set_aspect('equal')
        ax.legend()
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')
        ax.set_aspect('equal')
        ax.grid(zorder = -10)
        
        if figax == None:
            plt.show()
        else:
            return fig, ax
    
    def get_unit_patches(self,xy:np.ndarray) -> list:
        """Get the patches of the PMT unit for plotting.

        Args:
            xy (np.ndarray): the coordinates of the bottom left corner of
                the PMT unit.

        Returns:
            list: list of patches of the PMT units
        """
        if self.type == 'circular':
            p = [Circle((xy[0], xy[1]),
                        radius = self.radius,
                        facecolor = 'gray',
                        alpha = 0.3, edgecolor = 'k', zorder = 1),
                 Circle((xy[0], xy[1]),
                        radius = self.active_radius,
                        facecolor = 'k', alpha = 0.98, edgecolor = 'k', zorder = 2)
                ]
            
        elif self.type == 'square':
            p = [Rectangle((xy[0]+self.width_tolerance, 
                            xy[1]+self.height_tolerance), 
                        width=self.width,
                        height=self.height,
                        facecolor = 'gray',
                        alpha = 0.3, edgecolor = 'k', zorder = 3),
                Rectangle((xy[0]+self.D_corner_x_active,
                            xy[1]+self.D_corner_y_active), 
                        width=self.width_active, 
                        height=self.height_active, 
                        facecolor = 'k', alpha = 0.98, 
                        edgecolor = 'k', zorder = 4)
                ]
        return p
    
    def plot_round_model(self, xy = (0,0), figax = None):
        """Make a plot of the PMT unit model

        Args:
            xy (tuple, optional): coordinates of the bottom left corner. 
                Defaults to (0,0).
            figax (_type_, optional): figure and axis environment. 
                Defaults to None.

        Returns:
            _type_: updated figure and axis environment
        """

        if self.type != 'circular':
            raise ValueError('This plotting function is for type circular PMTs.')
        
        if figax == None:
            fig, ax = plt.subplots(1,1,figsize = (5,5))
        
        ax.add_patch(Circle((xy[0], xy[1]),
                            radius = self.radius,
                            facecolor = 'gray',
                            alpha = 0.3, edgecolor = 'k',
                            label = 'Packaging area', zorder = 1))
        ax.add_patch(Circle((xy[0], xy[1]),
                            radius = self.active_radius,
                            facecolor = 'k', alpha = 0.8, edgecolor = 'k',
                            label = 'Active area', zorder = 2))
        geometric_centre = self.get_unit_centre()
        active_centre = self.get_unit_active_centre()

        ax.plot(geometric_centre[0], geometric_centre[1], 'o', 
                c = 'g', label = 'Geometric centre')
        ax.plot(active_centre[0], active_centre[1], 'x',
                c = 'r', label = 'Active centre')
        
        ax.set_xlim(xy[0]-1.1*self.radius, xy[0]+1.1*self.radius)
        ax.set_ylim(xy[1]-1.1*self.radius, xy[1]+1.1*self.radius)
        ax.set_aspect('equal')
        fig.legend()
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')
        ax.set_aspect('equal')
        ax.grid(zorder = -10)
        
        if figax == None:
            plt.show()
        else:
            return fig, ax


    
    def print_properties(self) -> None:
        """Print the main properties of the PMT model
        """
        print('---------------------------')
        print(f'Model: {self.name}')
        print('---------------------------')

        if self.type == 'circular':
            print(f'Diameter: {self.diameter_packaging} mm')
            print(f'Active diameter: {self.active_diameter} mm')
            print(f'Diameter tolerance: {self.diameter_tolerance} mm')

        elif self.type == 'square':
            print(f'Width: {self.width} mm')
            print(f'Height: {self.height} mm')
            print(f'Active width: {self.width_active} mm')
            print(f'Active height: {self.height_active} mm')
            print(f'Width tolerance: {self.width_tolerance} mm')
            print(f'Height tolerance: {self.height_tolerance} mm')
        
        print('---------------------------')
        print(f'Total unit area: {self.total_area:.2f} mm^2')
        print(f'Active area geometric correction: '
              f'{self.active_area_correction:.2f}')
        print(f'Active area: {self.active_area:.2f} mm^2')
        print(f'Active area fraction: '
              f'{self.active_area_fraction:.2f}')
