#!/usr/bin/env python

# TODO: setup logging

import os
from optparse import OptionParser, OptionGroup
import yaml
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.lines as mlines

from pulsar_spectra.load_data import DEFAULT_PLOTTING_CONFIG, DEFAULT_MARKER_CSV


def parse_opts():
    parser = OptionParser(usage='Usage: %prog [options]',
                          description='Create a plotting configuration file.')
    
    output_options = OptionGroup(parser, 'Output Options')
    output_options.add_option('-F', '--filename',
                  action='store', type='string', dest='output_file', default=DEFAULT_PLOTTING_CONFIG,
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
    # TODO: work out how to input custom linestyle: (0, (0.7, 1))
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
    marker_config.add_option('--marker_scale',
                  action='store', type='float', dest='marker_scale', default=0.7,
                  help='Scaling factor for marker size [default: %default]')
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
    config["Markers"] = []
    marker_styles = np.loadtxt(opts.marker_file, delimiter=',', dtype=str, comments='%')
    for style in marker_styles:
        if not is_valid_colour(style[0]) and not is_valid_marker(style[1]):
            print(f'Error: invalid marker style - {style} (skipping)')
            continue
        if style[3] == '':
            desc = 'Unlabelled'
        else:
            desc = str(style[3])
        config["Markers"].append([desc, str(style[0]), str(style[1]), round(float(style[2])*opts.marker_scale,2)])

    with open(opts.output_file, 'w') as f:
        yaml.dump(config, f, sort_keys=False)


if __name__ == '__main__':
    main()