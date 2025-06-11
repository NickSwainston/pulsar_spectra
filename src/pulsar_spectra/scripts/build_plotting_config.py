#!/usr/bin/env python

# TODO: setup logging
# TODO: work out how to get user input for custom linestyle: e.g. (0, (0.7, 1))

import os
import csv
import random
import yaml
import argparse
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


def parse_args():
    parser = argparse.ArgumentParser(usage='Usage: %(prog)s [options]',
                          description='Create a plotting configuration file.')
    
    output_options = parser.add_argument_group('Output')
    output_options.add_argument('-F', '--filename',
                  action='store', type=str, dest='output_file', default='plotting_config.yaml',
                  help='Location of output configuration file to write to [default: %(default)s]')

    figure_config = parser.add_argument_group('Figure Configuration')
    figure_config.add_argument('-H', '--fig_height',
                  action='store', type=float, dest='fig_height', default=3.2,
                  help='Height of figure in inches [default: %(default)s]')
    figure_config.add_argument('-R', '--aspect_ratio',
                  action='store', type=str, dest='aspect_ratio', default='4x3',
                  help='Aspect ratio (WxH) [default: %(default)s]')
    figure_config.add_argument('--dpi',
                  action='store', type=int, dest='dpi', default=300,
                  help='Resolution of figure in dots-per-inch [default: %(default)s]')

    model_config = parser.add_argument_group('Model Configuration')
    model_config.add_argument('--primary_ls',
                  action='store', type=str, dest='primary_ls',
                  default='--',
                  help='Line style of primary model curve [default: %(default)s]')
    model_config.add_argument('--secondary_ls',
                  action='store', type=str, dest='secondary_ls',
                  default=':',
                  help='Line style of secondary model curve [default: %(default)s]')
    model_config.add_argument('--model_colour',
                  action='store', type=str, dest='model_colour',
                  default='k',
                  help='Colour of the model curves [default: %(default)s]')
    model_config.add_argument('--model_error_colour',
                  action='store', type=str, dest='model_error_colour',
                  default='C1',
                  help='Colour of the model error region [default: %(default)s]')
    
    marker_config = parser.add_argument_group('Marker Configuration')
    marker_config.add_argument('--marker_file',
                  action='store', type=str, dest='marker_file',
                  default=DEFAULT_MARKER_CSV,
                  help='List of marker styles [default: %(default)s]')
    marker_config.add_argument('--marker_size',
                  action='store', type=float, dest='marker_size', default=4.5,
                  help='Marker size [default: %(default)s]')
    marker_config.add_argument('--marker_border_lw',
                  action='store', type=float, dest='marker_border_lw', default=0.5,
                  help='Marker border thickness [default: %(default)s]')
    marker_config.add_argument('--capsize',
                  action='store', type=float, dest='capsize', default=1.5,
                  help='Marker cap size [default: %(default)s]')
    marker_config.add_argument('--errorbar_lw',
                  action='store', type=float, dest='errorbar_lw', default=0.7,
                  help='Errorbar line width [default: %(default)s]')

    marker_generation = parser.add_argument_group('Marker Generation')
    marker_generation.add_argument('-g', '--generate_markers',
                  action='store_true', dest='generate', default=False,
                  help='Generate a set of unique markers.')
    marker_generation.add_argument('--shuffle',
                  action='store_true', dest='shuffle', default=False,
                  help='Randomise the marker colour/type order.')
    marker_generation.add_argument('--no_scaling',
                  action='store_false', dest='uniform_size', default=True,
                  help='Do not use perceptually uniform marker sizes.')
    marker_generation.add_argument('--marker_preview',
                  action='store_true', dest='plot_preview', default=False,
                  help='Plot a preview of the generated marker types.')
    marker_generation.add_argument('--num_markers',
                  action='store', type=int, dest='num_markers', default=30,
                  help='Number of unique markers to generate [default: %(default)s]')
    marker_generation.add_argument('--palette',
                  action='store', type=str, dest='palette',
                  default='TAB',
                  help="Colour palette to use (Available: 'TAB', 'IBM', 'WONG') [default: %(default)s]")
    marker_generation.add_argument('--marker_file_savename',
                  action='store', type=str, dest='marker_file_savename',
                  default=None,
                  help='Write generated markers to the specified file [default: %(default)s]')
    marker_generation.add_argument('-p', '--pulsars',
                  type=str, dest='psrs', nargs='*',
                  help='Space seperated list of pulsar J names. ' + \
                  'If given, will assign a unique marker to every publication in the pulsar set.')
    
    args = parser.parse_args()

    if not os.path.isfile(args.marker_file):
        parser.error('cannot locate marker style file')

    if len(args.aspect_ratio.split('x')) != 2:
        parser.error('invalid aspect ratio')

    if not is_valid_colour(args.model_colour):
        parser.error(f'invalid model colour')

    if not is_valid_colour(args.model_error_colour):
        parser.error(f'invalid model error colour')

    return args


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

    if plot_preview:
        # Preview markers as a sinusoid
        fig, ax = plt.subplots(figsize=(4,2))
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim([-1.5, 1.5])
        phases_to_plot = num_markers//50 + 1
        x_arr = np.arange(num_markers)*2*np.pi/num_markers*phases_to_plot
        y_arr = np.sin(x_arr)

    max_unique_markers = len(palette) * len(MARKERS)
    if num_markers > max_unique_markers:
        print(f'Warning: Only {max_unique_markers} unique markers are possible.')
        num_markers = max_unique_markers

    unique_markers = []
    num_left_to_generate = num_markers
    while num_left_to_generate > 0:
        generate_on_current_loop = num_left_to_generate

        if shuffle:
            random.shuffle(palette)
            random.shuffle(MARKERS)

        if num_markers < len(palette):
            colours = palette[0:num_markers]
        else:
            if shuffle:
                colours = []
                for _ in range(num_markers//len(palette)):
                    colours += palette
                    random.shuffle(palette)
                colours += palette[0:len(palette)%num_markers]
            else:
                colours = (num_markers//len(palette))*palette + palette[0:len(palette)%num_markers]

        if num_markers < len(MARKERS):
            markers = MARKERS[0:num_markers]
        else:
            if shuffle:
                markers = []
                for _ in range(num_markers//len(MARKERS)):
                    markers += MARKERS
                    random.shuffle(MARKERS)
                markers += MARKERS[0:len(MARKERS)%num_markers]
            else:
                markers = (num_markers//len(MARKERS))*MARKERS + MARKERS[0:len(MARKERS)%num_markers]
    
        for i in range(generate_on_current_loop):
            if uniform_size:
                marker = [f'{colours[i][1]} {markers[i][2]}', colours[i][0], markers[i][0], round(marker_size*markers[i][1], 2)]
            else:
                marker = [f'{colours[i][1]} {markers[i][2]}', colours[i][0], markers[i][0], round(marker_size, 2)]
            if marker in unique_markers:
                # print(f'Duplicate marker skipped: {marker}')
                continue
            else:
                num_left_to_generate -= 1
            unique_markers.append(marker)
    
    print(f'{len(unique_markers)} unique markers generated')

    if plot_preview:
        for i, marker in enumerate(unique_markers):
            ax.errorbar(
                x_arr[i],
                y_arr[i],
                yerr=[0.1],
                xerr=[0.1],
                c=marker[1],
                marker=marker[2],
                ms=marker[3],
                ls=None,
                mec='k',
                mew=0.5,
                elinewidth=0.7,
                capsize=1.5,
            )

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


def create_ref_marker_combinations(psrs, args):
    from pulsar_spectra.catalogue import collect_catalogue_fluxes

    cat_dict = collect_catalogue_fluxes()
    all_refs = []
    for psr in psrs:
        _, _, _, _, refs = cat_dict[psr]
        all_refs += refs
    unique_refs = list(np.unique(np.array(all_refs)))
    num_unique_refs = len(unique_refs)

    markers = generate_marker_set(num_unique_refs, args.marker_size,
            args.palette, args.shuffle, args.uniform_size, args.plot_preview,
            args.marker_file_savename)
    
    ref_markers = {}
    for i, ref in enumerate(unique_refs):
        ref_markers[ref] = [markers[i][1], markers[i][2], markers[i][3]]

    return markers, ref_markers


def main():
    args = parse_args()

    config = {}

    config["Figure height"] = args.fig_height
    config["Aspect ratio"] = float(args.aspect_ratio.split('x')[0]) / float(args.aspect_ratio.split('x')[1])
    config["Resolution"] = args.dpi
    config["Primary linestyle"] = args.primary_ls
    config["Secondary linestyle"] = args.secondary_ls
    config["Model colour"] = args.model_colour
    config["Model error colour"] = args.model_error_colour
    config["Marker border"] = args.marker_border_lw
    config["Capsize"] = args.capsize
    config["Errorbar linewidth"] = args.errorbar_lw

    if args.psrs is not None:
        markers, ref_markers = create_ref_marker_combinations(args.psrs, args)
        with open('ref_markers.yaml', 'w') as f:
            yaml.dump(ref_markers, f, sort_keys=False)
    else:
        if args.generate:
            markers = generate_marker_set(args.num_markers, args.marker_size,
                args.palette, args.shuffle, args.uniform_size, args.plot_preview,
                args.marker_file_savename)
        else:
            markers = []
            marker_styles = np.loadtxt(args.marker_file, delimiter=',', dtype=str, comments='%')
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

    with open(args.output_file, 'w') as f:
        yaml.dump(config, f, sort_keys=False)


if __name__ == '__main__':
    main()