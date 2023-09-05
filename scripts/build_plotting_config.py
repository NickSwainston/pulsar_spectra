#!/usr/bin/env python

# TODO: setup logging
# TODO: work out how to get user input for custom linestyle: e.g. (0, (0.7, 1))

import os
import csv
import random
import yaml
from optparse import OptionParser, OptionGroup
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.lines as mlines
import matplotlib.pyplot as plt

from pulsar_spectra.load_data import DEFAULT_MARKER_CSV


# [colour, description]
# Standard matplotlib colours
PALETTE_TABLEAU = [
    ['tab:blue', 'blue'],
    ['tab:orange', 'orange'],
    ['tab:green', 'green'],
    ['tab:purple', 'purple'],
    ['tab:brown', 'brown'],
    ['tab:pink', 'pink'],
    ['tab:gray', 'grey'],
    ['tab:olive', 'olive'],
    ['tab:cyan', 'cyan'],
]

# ref: https://davidmathlogic.com/colorblind/
PALETTE_IBM = [
    ['#648FFF', 'blue'],
    ['#785EF0', 'dark lavender'],
    ['#DC267F', 'deep pink'],
    ['#FE6100', 'dark orange'],
    ['#FFB000', 'orange'],
    ['#FDDF49', 'yellow'],
    ['#8FB327', 'lime green'],
    ['#902499', 'purple'],
    ['#17E474', 'lime'],
    ['#74CE22', 'green'],
    ['#449C8C', 'teal'],
    ['#EA83B7', 'pink'],
]
# ref: https://davidmathlogic.com/colorblind/
PALETTE_WONG = [
    ['#DF0A10', 'red'],
    ['#E69F00', 'orange'],
    ['#56B4E9', 'sky blue'],
    ['#009E73', 'sea green'],
    ['#F0E442', 'yellow'],
    ['#0072B2', 'blue'],
    ['#D55E00', 'dark orange'],
    ['#CC79A7', 'pink'],
    ['#80C774', 'lime green'],
    ['#A21DCA', 'purple'],
    ['#9BFB5F', 'lawn green'],
    ['#BDD1D2', 'grey'],
]

# [marker_type, size_scale, description]
MARKERS = [
    ['o', 0.95, 'circle'],
    ['v', 1, 'down-pointing triangle'],
    ['^', 1, 'up-pointing triangle'],
    ['<', 1, 'left-pointing triangle'],
    ['>', 1, 'right-pointing triangle'],
    ['8', 1, 'octagon'],
    ['s', 0.9, 'square'],
    ['p', 1, 'pentagon'],
    ['P', 1.2, 'plus'],
    ['*', 1.5, 'star'],
    ['h', 1, 'hexagon'],
    ['H', 1, 'rotated hexagon'],
    ['X', 1, 'cross'],
    ['D', 0.75, 'diamond'],
    ['d', 0.9, 'thin diamond'],
]


def parse_opts():
    parser = OptionParser(usage='Usage: %prog [options]',
                          description='Create a plotting configuration file.')
    
    output_options = OptionGroup(parser, 'Output Options')
    output_options.add_option('-F', '--filename',
                  action='store', type='string', dest='output_file', default='plotting_config.yaml',
                  help='Location of output configuration file to write to [default: %default]')
    parser.add_option_group(output_options)

    figure_config = OptionGroup(parser, 'Figure Configuration')
    figure_config.add_option('-H', '--fig_height',
                  action='store', type='float', dest='fig_height', default=3.2,
                  help='Height of figure in inches [default: %default]')
    figure_config.add_option('-R', '--aspect_ratio',
                  action='store', type='string', dest='aspect_ratio', default='4x3',
                  help='Aspect ratio (WxH) [default: %default]')
    figure_config.add_option('--dpi',
                  action='store', type='int', dest='dpi', default=300,
                  help='Resolution of figure in dots-per-inch [default: %default]')
    parser.add_option_group(figure_config)

    model_config = OptionGroup(parser, 'Model Configuration')
    model_config.add_option('--primary_ls',
                  action='store', type='string', dest='primary_ls',
                  default='--',
                  help='Line style of primary model curve [default: %default]')
    model_config.add_option('--secondary_ls',
                  action='store', type='string', dest='secondary_ls',
                  default=':',
                  help='Line style of secondary model curve [default: %default]')
    model_config.add_option('--model_colour',
                  action='store', type='string', dest='model_colour',
                  default='k',
                  help='Colour of the model curves [default: %default]')
    model_config.add_option('--model_error_colour',
                  action='store', type='string', dest='model_error_colour',
                  default='C1',
                  help='Colour of the model error region [default: %default]')
    parser.add_option_group(model_config)
    
    marker_config = OptionGroup(parser, 'Marker Configuration')
    marker_config.add_option('--marker_file',
                  action='store', type='string', dest='marker_file',
                  default=DEFAULT_MARKER_CSV,
                  help='List of marker styles [default: %default]')
    marker_config.add_option('--marker_size',
                  action='store', type='float', dest='marker_size', default=4.5,
                  help='Marker size [default: %default]')
    marker_config.add_option('--marker_border_lw',
                  action='store', type='float', dest='marker_border_lw', default=0.5,
                  help='Marker border thickness [default: %default]')
    marker_config.add_option('--capsize',
                  action='store', type='float', dest='capsize', default=1.5,
                  help='Marker cap size [default: %default]')
    marker_config.add_option('--errorbar_lw',
                  action='store', type='float', dest='errorbar_lw', default=0.7,
                  help='Errorbar line width [default: %default]')
    parser.add_option_group(marker_config)

    marker_generation = OptionGroup(parser, 'Marker Generation Options')
    marker_generation.add_option('-g', '--generate_markers',
                  action='store_true', dest='generate', default=False,
                  help='Generate a set of unique markers.')
    marker_generation.add_option('--shuffle',
                  action='store_true', dest='shuffle', default=False,
                  help='Randomise the marker colour/type order.')
    marker_generation.add_option('--no_scaling',
                  action='store_false', dest='uniform_size', default=True,
                  help='Do not use perceptually uniform marker sizes.')
    marker_generation.add_option('--marker_preview',
                  action='store_true', dest='plot_preview', default=False,
                  help='Plot a preview of the generated marker types.')
    marker_generation.add_option('--num_markers',
                  action='store', type='int', dest='num_markers', default=30,
                  help='Number of unique markers to generate [default: %default]')
    marker_generation.add_option('--palette',
                  action='store', type='string', dest='palette',
                  default='TAB',
                  help="Colour palette to use (Available: 'TAB', 'IBM', 'WONG') [default: %default]")
    marker_generation.add_option('--marker_file_savename',
                  action='store', type='string', dest='marker_file_savename',
                  default=None,
                  help='Write generated markers to the specified file [default: %default]')
    parser.add_option_group(marker_generation)
    
    (opts, _) = parser.parse_args()

    if not os.path.isfile(opts.marker_file):
        parser.error('cannot locate marker style file')

    if len(opts.aspect_ratio.split('x')) != 2:
        parser.error('invalid aspect ratio')

    if not is_valid_colour(opts.model_colour):
        parser.error(f'invalid model colour')

    if not is_valid_colour(opts.model_error_colour):
        parser.error(f'invalid model error colour')

    return opts


def is_valid_colour(colour_string):
    try:
        mcolors.to_rgba(colour_string)
        return True
    except ValueError:
        try:
            mcolors.to_rgba('#' + colour_string)
            return True
        except ValueError:
            return False
        

def is_valid_marker(marker_string):
    valid_markers = mlines.Line2D.markers.keys()
    return marker_string in valid_markers


def generate_marker_set(num_markers, marker_size, palette_name='IBM',
                        shuffle=True, uniform_size=True, plot_preview=False,
                        savename=None):
    if palette_name == 'TAB':
        palette = PALETTE_TABLEAU
    elif palette_name == 'IBM':
        palette = PALETTE_IBM
    elif palette_name == 'WONG':
        palette = PALETTE_WONG
    else:
        print(f'Error: palette name not valid. Defaulting to IBM.')
        palette = PALETTE_IBM

    if shuffle:
        random.shuffle(palette)
        random.shuffle(MARKERS)

    if num_markers < len(palette):
        colours = palette[0:num_markers]
    else:
        colours = (num_markers//len(palette))*palette + palette[0:len(palette)%num_markers]

    if num_markers < len(MARKERS):
        markers = MARKERS[0:num_markers]
    else:
        markers = (num_markers//len(MARKERS))*MARKERS + MARKERS[0:len(MARKERS)%num_markers]

    if plot_preview:
        # Preview markers as a sinusoid
        fig, ax = plt.subplots(figsize=(4,2))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim([-1.5, 1.5])
        x_arr = np.arange(num_markers)*2*np.pi/num_markers
        y_arr = np.sin(x_arr)
    
    unique_markers = []
    for i in range(num_markers):
        if uniform_size:
            marker = [f'{colours[i][1]} {markers[i][2]}', colours[i][0], markers[i][0], round(marker_size*markers[i][1], 2)]
        else:
            marker = [f'{colours[i][1]} {markers[i][2]}', colours[i][0], markers[i][0], round(marker_size, 2)]
        if marker in unique_markers:
            print(f'Duplicate marker skipped: {marker}')
            continue
        unique_markers.append(marker)
        
        if plot_preview:
            ax.errorbar(
                x_arr[i],
                y_arr[i],
                yerr=0.1,
                xerr=0.1,
                c=marker[1],
                marker=marker[2],
                ms=marker[3],
                ls=None,
                mec='k',
                mew=0.5,
                elinewidth=0.7,
                capsize=1.5,
            )
    print(f'{len(unique_markers)} unique markers generated')

    if savename:
        with open(savename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['%marker_colour', 'marker_type', 'marker_size', 'description'])
            for marker in unique_markers:
                writer.writerow([marker[1], marker[2], marker[3], marker[0]])
    
    if plot_preview:
        plt.savefig(f'marker_preview.png', dpi=300, bbox_inches='tight')
        plt.clf()

    return unique_markers


def main():
    opts = parse_opts()

    config = {}

    config["Figure height"] = opts.fig_height
    config["Aspect ratio"] = float(opts.aspect_ratio.split('x')[0]) / float(opts.aspect_ratio.split('x')[1])
    config["Resolution"] = opts.dpi
    config["Primary linestyle"] = opts.primary_ls
    config["Secondary linestyle"] = opts.secondary_ls
    config["Model colour"] = opts.model_colour
    config["Model error colour"] = opts.model_error_colour
    config["Marker border"] = opts.marker_border_lw
    config["Capsize"] = opts.capsize
    config["Errorbar linewidth"] = opts.errorbar_lw

    if opts.generate:
        markers = generate_marker_set(opts.num_markers, opts.marker_size,
            opts.palette, opts.shuffle, opts.uniform_size, opts.plot_preview,
            opts.marker_file_savename)
    else:
        markers = []
        marker_styles = np.loadtxt(opts.marker_file, delimiter=',', dtype=str, comments='%')
        for style in marker_styles:
            if not is_valid_colour(style[0]) and not is_valid_marker(style[1]):
                print(f'Error: invalid marker style - {style} (skipping)')
                continue
            if style[3] == '':
                desc = 'Unlabelled'
            else:
                desc = str(style[3])
            markers.append([desc, str(style[0]), str(style[1]), round(float(style[2]),2)])

    config["Markers"] = markers

    with open(opts.output_file, 'w') as f:
        yaml.dump(config, f, sort_keys=False)


if __name__ == '__main__':
    main()