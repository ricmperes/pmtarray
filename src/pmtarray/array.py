import matplotlib.pyplot as plt
import numpy as np
from hexalattice.hexalattice import create_hex_grid
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle

from pmtarray.unit import PMTunit


class PMTarray():
    """Class to represent a PMT array.
    """
    def __init__(self, array_diameter: float,
                 border_margin:float, intra_pmt_distance:float,
                 pmt_model:str,
                 custom_unit_params:dict = {}):
        """PMTarray class

        Args:
            array_diameter (float): diameter of the array
            border_margin (float): margin between the PMTs and the array border
            pmt_model (str): model of the PMT to use
            custom_unit_params (dict, optional): dictionary with custom 
                parameters for the PMT unit. Defaults to {}.
        """
        
        self.array_diameter = array_diameter
        self.border_margin = border_margin
        self.pmtunit = self.load_pmtunit(pmt_model, custom_unit_params)
        self.intra_pmt_distance = intra_pmt_distance

        if self.pmtunit.type == 'square':
            corner_meshes = self.make_square_corners()
            self.cut_square_outside_array(corner_meshes)
            self.n_pmts = self.A_corners_xx.count()

        if self.pmtunit.type == 'circular':
            self.set_hex_array_positions()
            self.n_pmts = len(self.hex_array_centers_x)

        self.total_array_area = np.pi * (self.array_diameter/2)**2
        self.total_pmt_area = self.n_pmts * self.pmtunit.total_area
        self.total_pmt_active_area = self.n_pmts * self.pmtunit.active_area
        self.pmt_coverage = self.total_pmt_active_area/self.total_array_area


    def set_hex_array_positions(self):
        """Set the positions of the PMTs in a hexagonal grid.
        Makes use of the hexalattice pacakge for the base grid."""

        r_max = self.array_diameter/2 - self.border_margin

        n_hex_x = np.ceil((self.array_diameter + np.abs(self.border_margin))/
                          (self.pmtunit.diameter_packaging + 
                           self.pmtunit.diameter_tolerance)*1.2)
        n_hex_y = np.ceil((self.array_diameter+ np.abs(self.border_margin))/
                          (4/np.sqrt(3)*
                           (np.ceil((self.pmtunit.diameter_packaging)/4))
                                     )*1.2)

        hex_centers, _ = create_hex_grid(
            nx=n_hex_x, ny=n_hex_y,
            min_diam = self.pmtunit.diameter_packaging+self.intra_pmt_distance,
            crop_circ = r_max - self.pmtunit.diameter_packaging/2-self.border_margin,
            do_plot = False,
            plotting_gap=(self.intra_pmt_distance/
                          (self.pmtunit.diameter_packaging+self.intra_pmt_distance)
                          ))
        
        hex_centers_x = hex_centers[:, 0]
        hex_centers_y = hex_centers[:, 1]

        self.hex_array_centers_x = hex_centers_x
        self.hex_array_centers_y = hex_centers_y

    def make_square_corners(self) -> tuple:
        """Define where the corners of the PMTs are

        Returns:
            tuple: (A_corner_xx, A_corner_yy, B_corner_xx, B_corner_yy, 
                        C_corner_xx, C_corner_yy, D_corner_xx, D_corner_yy)
        """
        
        # make the center a not
        D_corner_x = np.arange(
            0 + self.intra_pmt_distance/2, 
            self.array_diameter/2 + self.pmtunit.width_unit + self.intra_pmt_distance, 
            self.pmtunit.width_unit + self.intra_pmt_distance)
        D_corner_y = np.arange(
            0 + self.intra_pmt_distance/2,
            self.array_diameter/2 + self.pmtunit.height_unit + self.intra_pmt_distance, 
            self.pmtunit.height_unit + self.intra_pmt_distance)

        D_corner_x = np.concatenate(
            [-np.flip(D_corner_x) - self.pmtunit.width_unit,
             D_corner_x])
        D_corner_y = np.concatenate(
            [-np.flip(D_corner_y) - self.pmtunit.height_unit,
             D_corner_y])

        D_corner_xx, D_corner_yy = np.meshgrid(D_corner_x, D_corner_y, indexing = 'ij') 

        A_corner_xx = D_corner_xx
        A_corner_yy = B_corner_yy = D_corner_yy + self.pmtunit.height_unit

        B_corner_xx = C_corner_xx = D_corner_xx + self.pmtunit.width_unit
        C_corner_yy = D_corner_yy
        
        return (A_corner_xx, A_corner_yy, B_corner_xx, B_corner_yy, 
                C_corner_xx, C_corner_yy, D_corner_xx, D_corner_yy)
    
    def cut_square_outside_array(self, corner_meshes:tuple):
        """Mask the PMTs that are outside the array in a masked array.

        Args:
            corner_meshes (tuple): tuple with all the corner meshes
        """        
        (A_corner_xx, A_corner_yy, B_corner_xx, B_corner_yy, 
                C_corner_xx, C_corner_yy, D_corner_xx, D_corner_yy) = corner_meshes
        D_corner_rr = np.sqrt(D_corner_xx**2 + D_corner_yy**2)

        A_corner_rr = np.sqrt(A_corner_xx**2 + A_corner_yy**2)
        B_corner_rr = np.sqrt(B_corner_xx**2 + B_corner_yy**2)
        C_corner_rr = np.sqrt(C_corner_xx**2 + C_corner_yy**2)
        
        A_mask_inside_array_rr = A_corner_rr < self.array_diameter/2 - self.border_margin
        B_mask_inside_array_rr = B_corner_rr < self.array_diameter/2 - self.border_margin
        C_mask_inside_array_rr = C_corner_rr < self.array_diameter/2 - self.border_margin
        D_mask_inside_array_rr = D_corner_rr < self.array_diameter/2 - self.border_margin
        
        merged_mask = (~A_mask_inside_array_rr | 
                       ~B_mask_inside_array_rr | 
                       ~C_mask_inside_array_rr | 
                       ~D_mask_inside_array_rr)
        
        self.D_corners_xx = np.ma.masked_array(D_corner_xx, mask= merged_mask)
        self.D_corners_yy = np.ma.masked_array(D_corner_yy, mask= merged_mask)

        self.A_corners_xx = np.ma.masked_array(A_corner_xx, mask= merged_mask)
        self.A_corners_yy = np.ma.masked_array(A_corner_yy, mask= merged_mask)

        self.B_corners_xx = np.ma.masked_array(B_corner_xx, mask= merged_mask)
        self.B_corners_yy = np.ma.masked_array(B_corner_yy, mask= merged_mask)

        self.C_corners_xx = np.ma.masked_array(C_corner_xx, mask= merged_mask)
        self.C_corners_yy = np.ma.masked_array(C_corner_yy, mask= merged_mask)
    
    def load_pmtunit(self, model: str, custom_unit_params: dict = {}):
        """Load the PMT unit.

        Args:
            model (str): name of the PMT model

        Returns:
            PMTunit: a PMT unit class object
        """
        return PMTunit(model=model, custom_params=custom_unit_params)
    
    def get_square_centres(self, active_area: bool = True):
        """Get centres of the PMTs.

        Args:
            active_area (bool, optional): Returns the centres of teh 
                active areas if true, otherwise the geometric centres of 
                the packaging if false. Defaults to True.
        Retuns:
            list: list of the centres of the PMTs
        """
        if active_area:
            (x_pmt_centre, y_pmt_centre) = self.pmtunit.get_unit_active_centre()
        else:
            (x_pmt_centre, y_pmt_centre) = self.pmtunit.get_unit_centre()
        
        D_corners_x_flatten = self.D_corners_xx.flatten().compressed()
        D_corners_y_flatten = self.D_corners_yy.flatten().compressed()

        xs = D_corners_x_flatten + x_pmt_centre
        ys = D_corners_y_flatten + y_pmt_centre

        return np.vstack((xs, ys))
    
    def export_centres(self, file_name, active_area: bool = True) -> None:
        """Export the centres of the PMTs to a file.

        Args:
            file_name (str): name of the file to write the centres into
        """
        if self.pmtunit.type == 'square':
            centres = self.get_square_centres(active_area=active_area)
        
        elif self.pmtunit.type == 'circular':
            centres = np.vstack((self.hex_array_centers_x, 
                                 self.hex_array_centers_y))
        np.savetxt(file_name, 
                   centres.T, 
                   header = 'x, y',
                   delimiter=", ", 
                   fmt='%.3f')
    
    def get_corners_active(self) -> np.ndarray:
        """Get all the positions of the corners of the active area of the PMTs.

        Returns:
            np.ndarray: an array with the x and y coordinates of the 
                corners of the active area of the PMTs
        """
        
        A_corner_x = (self.D_corners_xx.flatten().compressed() + 
                        self.pmtunit.D_corner_x_active)
        B_corner_x = (self.D_corners_xx.flatten().compressed() + 
                        self.pmtunit.D_corner_x_active +
                        self.pmtunit.width_active)
        C_corner_x = (self.D_corners_xx.flatten().compressed() + 
                        self.pmtunit.D_corner_x_active +
                        self.pmtunit.width_active)
        D_corner_x = (self.D_corners_xx.flatten().compressed() + 
                        self.pmtunit.D_corner_x_active)
        A_corner_y = (self.D_corners_yy.flatten().compressed() + 
                        self.pmtunit.D_corner_y_active + 
                        self.pmtunit.height_active)
        B_corner_y = (self.D_corners_yy.flatten().compressed() + 
                        self.pmtunit.D_corner_y_active + 
                        self.pmtunit.height_active)
        C_corner_y = (self.D_corners_yy.flatten().compressed() + 
                        self.pmtunit.D_corner_y_active)
        D_corner_y = (self.D_corners_yy.flatten().compressed() + 
                        self.pmtunit.D_corner_y_active)
        
        corners = np.vstack((A_corner_x, A_corner_y, B_corner_x, B_corner_y,
                             C_corner_x, C_corner_y, D_corner_x, D_corner_y))
        
        return corners
    
    def export_corners_active(self,file_name:str):
        """Export the corners of the active area of the PMTs to a file.

        Args:
            file_name (str): name of the file to write the corners into
        """
        if self.pmtunit.type == 'circular':
            raise ValueError('Circular PMTs do not have corners...')
        
        corners = self.get_corners_active()
        np.savetxt(file_name, corners.T, 
                       header = 'A_x, A_y, B_x, B_y, C_x, C_y, D_x, D_y', 
                       delimiter=', ',
                       fmt = '%.3f')


    def get_corners_package(self) -> np.ndarray:
        """Get all the positions of the corners of the total (includes 
        packaging) area of the PMTs.

        Returns:
            np.ndarray: an array with the x and y coordinates of the 
                corners of the total area (including packaging) of the PMTs
        """
        
        A_corner_x = (self.A_corners_xx.flatten().compressed() + 
                        self.pmtunit.width_tolerance)
        B_corner_x = (self.B_corners_xx.flatten().compressed() -
                        self.pmtunit.width_tolerance)
        C_corner_x = (self.C_corners_xx.flatten().compressed() -
                        self.pmtunit.width_tolerance)
        D_corner_x = (self.D_corners_xx.flatten().compressed() +
                        self.pmtunit.width_tolerance)
        A_corner_y = (self.A_corners_yy.flatten().compressed() -
                        self.pmtunit.height_tolerance)
        B_corner_y = (self.B_corners_yy.flatten().compressed() -
                        self.pmtunit.height_tolerance)
        C_corner_y = (self.C_corners_yy.flatten().compressed() +
                        self.pmtunit.height_tolerance)
        D_corner_y = (self.D_corners_yy.flatten().compressed() +
                        self.pmtunit.height_tolerance)
        
        corners = np.vstack((A_corner_x, A_corner_y, B_corner_x, B_corner_y,
                             C_corner_x, C_corner_y, D_corner_x, D_corner_y))

        return corners
    
    def export_corners_package(self,file_name:str):
        """Export the corners of the total area of the PMTs to a file.

        Args:
            file_name (str): name of the file to write the corners into
        """
        if self.pmtunit.type == 'circular':
            raise ValueError('Circular PMTs do not have corners...')
        
        corners = self.get_corners_package()
        np.savetxt(file_name, 
                   corners.T, 
                   header = 'A_x, A_y, B_x, B_y, C_x, C_y, D_x, D_y', 
                   delimiter=', ',
                   fmt = '%.3f')
        
    def plot_square_pmt_array(self, figax:tuple = None):
        """Plot the array of pmts.

        Args:
            figax (tuple, optional): figure and axis objects to draw in. 
                Defaults to None.

        Returns:
            tuple: figure and axis objects
        """
        if figax is None:
            fig, ax = plt.subplots(figsize = (6,6))
        else:
            fig, ax = figax

        patches_pmts = []

        n_corner_x, n_corner_y = np.shape(self.D_corners_xx)

        for _x_i in range(n_corner_x):
            for _y_i in range(n_corner_y):
                patches_pmts += self.pmtunit.get_unit_patches(
                    (self.D_corners_xx[_x_i,_y_i], 
                     self.D_corners_yy[_x_i,_y_i]))
                
        ax.add_patch(Circle(xy=(0,0),
                            radius = self.array_diameter/2, 
                            fill = False, 
                            color = 'r',
                            zorder = 0, 
                            label = 'Array diameter'))

        p1 = PatchCollection(patches_pmts, match_original=True, 
                             label = 'PMT units 1')
        ax.add_collection(p1)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_aspect('equal')

        ax.set_xlim(-self.array_diameter*1.2/2,self.array_diameter*1.2/2)
        ax.set_ylim(-self.array_diameter*1.2/2,self.array_diameter*1.2/2)

        fig.legend()

        if figax is None:
            plt.show()
        else:
            return fig, ax
    
    def plot_circular_pmt_array(self, figax:tuple = None):
        """Plot the array of pmts.

        Args:
            figax (tuple, optional): figure and axis objects to draw in. 
                Defaults to None.

        Returns:
            tuple: figure and axis objects
        """
        if figax is None:
            fig, ax = plt.subplots(figsize = (6,6))
        else:
            fig, ax = figax

        patches_pmts = []

        for _x_i, _y_i in zip(self.hex_array_centers_x, self.hex_array_centers_y):
            patches_pmts += self.pmtunit.get_unit_patches((_x_i, _y_i))
                
        ax.add_patch(Circle(xy=(0,0),
                            radius = self.array_diameter/2, 
                            fill = False, 
                            color = 'r',
                            zorder = 0, 
                            label = 'Array diameter'))

        p1 = PatchCollection(patches_pmts, match_original=True, 
                             label = 'PMT units 1')
        ax.add_collection(p1)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_aspect('equal')

        ax.set_xlim(-self.array_diameter*1.2/2,self.array_diameter*1.2/2)
        ax.set_ylim(-self.array_diameter*1.2/2,self.array_diameter*1.2/2)

        fig.legend()

        if figax is None:
            plt.show()
        else:
            return fig, ax
        
    def plot_pmt_array(self, figax:tuple = None):
        """Plot the array of pmts.

        Args:
            figax (tuple, optional): figure and axis objects to draw in. 
                Defaults to None.

        Returns:
            tuple: figure and axis objects
        """
        if self.pmtunit.type == 'square':
            return self.plot_square_pmt_array(figax=figax)
        elif self.pmtunit.type == 'circular':
            return self.plot_circular_pmt_array(figax=figax)
        else:
            raise ValueError('PMT type not recognised')

    def print_properties(self, unit_properties = False):
        """Prints the main properties of the array object.

        Args:
            unit_properties (bool, optional): _description_. Defaults to False.
        """
        print(f'Array diameter: {self.array_diameter} mm')
        print(f'Margin from the array edge: {self.border_margin} mm')
        print(f'Number of units: {self.n_pmts}')
        print(f'Total array area: {self.total_array_area:.2f} mm^2')
        print(f'Total photosensor area: {self.total_pmt_area:.2f} mm^2')
        print(f'Total PMT active area: {self.total_pmt_active_area:.2f} mm^2')
        print(f'PMT coverage: {self.pmt_coverage:.2f}')

        if unit_properties:
            self.pmtunit.print_properties()
           