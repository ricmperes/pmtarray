#!/usr/bin/env python3

import argparse

import matplotlib.pyplot as plt

from pmtarray import PMTarray


def parse_args():
    parser = argparse.ArgumentParser(
        description=('Script to quickly get a PMT array plot or geometry.'))

    parser.add_argument('-m', '--model',
                        help='Define the PMT model.',
                        default= '6x6',
                        type = str,
                        required=True)
    parser.add_argument('-d', '--diameter',
                        help='Define the PMT array diameter in mm.',
                        required= True,
                        type= float)
    parser.add_argument('-b', '--border',
                        help='Define the PMT array border margin in mm.',
                        required= False,
                        type= float,
                        default= 0)
    parser.add_argument('-i','--intra_pmt_distance',
                        help='Define the distance between PMTs in mm.',
                        required= False,
                        type= float,
                        default= 0)
    parser.add_argument('-p', '--plot',
                        help='Plot the PMT array.',
                        type= bool,
                        default= False,
                        required=False)
    parser.add_argument('-o', '--output',
                        help ='Output the PMT array geometry to a file.',
                        type = bool,
                        default = True,
                        required=False)
    parser.add_argument('-v', '--verbose',
                        help ='Print the PMT array properties in the terminal.',
                        type = bool,
                        default = False,
                        required=False)
    args = parser.parse_args()

    model = args.model
    diameter = args.diameter
    border = args.border
    intra_pmt_distance = args.intra_pmt_distance
    plot = args.plot
    output = args.output
    verbose = args.verbose
    return model,diameter,border,intra_pmt_distance,plot,output,verbose

def make_plot(model, diameter, array):
    fig, ax = plt.subplots(1,1)
    fig, ax = array.plot_pmt_array(figax= (fig,ax))
    fig.savefig(f'pmtarray_{model}_{diameter}mm.png')

def make_output(model, diameter, array):
    if array.pmtunit.type == 'square':
        array.export_corners_active(
                file_name = f'pmtarray_corners_active_{model}_{diameter}mm.csv')
        array.export_corners_package(
                file_name = f'pmtarray_corners_package_{model}_{diameter}mm.csv')
    array.export_centres(
            file_name = f'pmtarray_centres_{model}_{diameter}mm.csv')

def main():
    model, diameter, border, intra_pmt_distance, plot, output, verbose = parse_args()
    if verbose: print('Building PMT array.')

    array = PMTarray(array_diameter = diameter, 
                      border_margin = border, 
                      pmt_model = model,
                      intra_pmt_distance = intra_pmt_distance)
    
    if verbose: array.print_properties(unit_properties=True)
    if plot: make_plot(model, diameter, array)
    if output: make_output(model, diameter, array)
    if verbose: print('Done!')

if __name__ == '__main__':
    main()


