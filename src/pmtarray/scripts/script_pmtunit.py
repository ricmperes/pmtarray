#!/usr/bin/env python3

import argparse

import matplotlib.pyplot as plt

from pmtarray import PMTunit


def main():
    model, plot, output, verbose = parse_args()

    if verbose: print('Building PMT array.')

    pmt_unit = PMTunit(model = model)
    
    if verbose: pmt_unit.print_properties()
    if plot: make_plot(model, pmt_unit)
    if output: raise NotImplementedError(
            'Output to file not implemented yet for single model.')
    if verbose: print('Done!')

def make_plot(model, pmt_unit):
    fig, ax = plt.subplots(1,1)
    fig, ax = pmt_unit.plot_model(figax = (fig, ax))
    fig.savefig(f'pmtunit_{model}.png')

def parse_args():
    parser = argparse.ArgumentParser(
        description=('Script to quickly get a PMT unit plot or geometry.'))

    parser.add_argument('-m', '--model',
                        help='Define the PMT model.',
                        default= '6x6',
                        type = str,
                        required=True)
    parser.add_argument('-p', '--plot',
                        help='Plot the PMT unit.',
                        type= bool,
                        default= False,
                        required=False)
    parser.add_argument('-o', '--output',
                        help ='Output the PMT unit geometry to a file.',
                        type = bool,
                        default = True,
                        required=False)
    parser.add_argument('-v', '--verbose',
                        help ='Print the PMT unit properties in the terminal.',
                        type = bool,
                        default = False,
                        required=False)
    args = parser.parse_args()

    model = args.model
    plot = args.plot
    output = args.output
    verbose = args.verbose
    return model,plot,output,verbose

if __name__ == '__main__':
    main()


