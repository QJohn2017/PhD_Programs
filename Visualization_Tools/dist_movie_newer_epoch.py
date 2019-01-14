import sdf
import glob
import numpy as np
from matplotlib import use
use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm
from matplotlib.ticker import FuncFormatter
import scipy.constants as sc
# plt.ion()


def get_si_prefix(scale, full_units=False):
    scale = abs(scale)
    mult = 1
    sym = ''

    if scale < 1e-24:
        full_units = True
    elif scale < 1e-21:
        # yocto
        mult = 1e24
        sym = 'y'
    elif scale < 1e-19:
        # zepto
        mult = 1e21
        sym = 'z'
    elif scale < 1e-16:
        # atto
        mult = 1e18
        sym = 'a'
    elif scale < 1e-13:
        # femto
        mult = 1e15
        sym = 'f'
    elif scale < 1e-10:
        # pico
        mult = 1e12
        sym = 'p'
    elif scale < 1e-7:
        # nano
        mult = 1e9
        sym = 'n'
    elif scale < 1e-4:
        # micro
        mult = 1e6
        sym = '{\mu}'
    elif scale < 1e-1:
        # milli
        mult = 1e3
        sym = 'm'
    elif scale >= 1e27:
        full_units = True
    elif scale >= 1e24:
        # yotta
        mult = 1e-24
        sym = 'Y'
    elif scale >= 1e21:
        # zetta
        mult = 1e-21
        sym = 'Z'
    elif scale >= 1e18:
        # exa
        mult = 1e-18
        sym = 'E'
    elif scale >= 1e15:
        # peta
        mult = 1e-15
        sym = 'P'
    elif scale >= 1e12:
        # tera
        mult = 1e-12
        sym = 'T'
    elif scale >= 1e9:
        # giga
        mult = 1e-9
        sym = 'G'
    elif scale >= 1e6:
        # mega
        mult = 1e-6
        sym = 'M'
    elif scale >= 1e3:
        # kilo
        mult = 1e-3
        sym = 'k'

    if full_units:
        scale = scale * mult
        if scale <= 0:
            pwr = 0
        else:
            pwr = (-np.floor(np.log10(scale)))

        mult = mult * np.power(10.0, pwr)
        if np.rint(pwr) != 0:
            sym = "(10^{%.0f})" % (-pwr) + sym

    return mult, sym


def get_var_range(file_list, varname):
    """Get a the data range for a given variable across an entire run"""

    vmin = float("inf")
    vmax = -float("inf")

    for f in file_list:
        try:
            data = sdf.read(f, mmap=0)
            var = data.__dict__[varname].data
            var_min = var.min()
            var_max = var.max()
            if var_min < vmin:
                vmin = var_min
            if var_max > vmax:
                vmax = var_max
        except:
            pass

    print vmin, vmax
    return vmin, vmax


def get_files(wkdir='Data', base=None):
    """Get a list of SDF filenames belonging to the same run"""
    import os.path

    if base:
        # take first element of base because parser gives args as a list
        wkdir = os.path.dirname(base[0])
        flist = glob.glob(wkdir + "/*.sdf")
        flist.remove(base[0])
        flist = base + sorted(flist)
    else:
        flist = glob.glob(wkdir + "/[0-9]*.sdf")
        flist = sorted(flist)

    # Find the job id
    # for f in flist:
    #     try:
    #         data = sdf.read(f, mmap=0)
    #         job_id = data.Header['jobid1']
    #         break
    #     except:
    #         pass

    # file_list = []

    # # Add all files matching the job id
    # for f in sorted(flist):
    #     try:
    #         data = sdf.read(f, mmap=0)
    #         file_job_id = data.Header['jobid1']
    #         # if file_job_id == job_id:
    #         file_list.append(f)
    #     except:
    #         pass

    return flist  # file_list


def clean_file_list(file_list, varname):
    new_file_list = []

    for f in file_list:
        try:
            data = sdf.read(f, mmap=0)
            dummy = data.__dict__[varname]
            new_file_list.append(f)
        except KeyError:
            pass
    return new_file_list


def plot_figure(filename, varname, vmin=None, vmax=None):
    """Plot the given variable for each file from a simulation"""
    global verbose

    if verbose > 1:
        print('Plotting {} from file {}'.format(varname, filename))

    fig = plt.figure()

    if verbose > 1:
        print('Reading data')
    data = sdf.read(filename, mmap=0)
    var = data.__dict__[varname]
    grid = var.grid
    vdata = var.data.T
    x = grid.data[0]
    y = np.copy(grid.data[1]) / (sc.value('electron volt') / sc.c)
    # y = grid.data[1]

    if verbose > 1:
        print('Plotting data')
    im = plt.pcolormesh(x, y, vdata, vmin=vmin, vmax=vmax)
    plt.title('step={}, time={}'.format(data.Header['step'],
                                        data.Header['time']))

    plt.axis('tight')

    # Get all labels for axes and data
    mult, sym = get_si_prefix(vmax - vmin)              # Data
    data_label = var.name + ' $(' + sym + var.units + ')$'
    xmult, xsym = get_si_prefix(np.max(x) - np.min(x))  # x axis
    ymult, ysym = get_si_prefix(np.max(y) - np.min(y))  # y axis

    if verbose > 1:
        print('Plotting axes')
    if verbose > 1:
        print('Scale axis by {} ({}, {})'.format(xmult, np.min(x), np.max(x)))

    ax = plt.gca()
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, y: (x * xmult)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, y: (x * ymult)))

    plt.xlabel(grid.labels[0] + ' $(' + xsym + grid.units[0] + ')$')
    plt.ylabel(grid.labels[1] + ' $(' + ysym + 'eV/c)$')
    # plt.ylabel(grid.labels[1] + ' $(' + ysym + grid.units[1] + ')$')

    # remove spines on right and top of plot
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # only show ticks on left and bottom side for these axes
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    # point ticks outside of plot
    ax.yaxis.set_tick_params(direction='out')
    ax.xaxis.set_tick_params(direction='out')

    if verbose > 1:
        print('Plotting colorbar')

    plt.colorbar(label=data_label, format=FuncFormatter(lambda x, y: x * mult)).ax.tick_params(axis='y', direction='out')
    plt.set_cmap(cm.coolwarm)

    if verbose > 1:
        print('Done plotting {} from file {}'.format(varname, filename))

    return im, fig


def plot_first_figure(file_list, varname, vmin=None, vmax=None):
    global verbose

    if verbose > 1:
        print('Getting data range')
    if vmin is None and vmax is None:
        vmin, vmax = get_var_range(file_list, varname)
    elif vmin is None:
        vmin = get_var_range(file_list, varname)[0]
    elif vmax is None:
        vmax = get_var_range(file_list, varname)[1]

    if verbose > 1:
        print('Found data range ({}, {})'.format(vmin, vmax))

    filename = file_list[0]
    im, fig = plot_figure(filename, varname, vmin, vmax)

    return im, fig


# def plot_figures(varname, scale=False, base=None):
# EDIT: ADD DIRECTORY AS OPTIONAL ARGUMENT
def plot_figures(varname, vmin=None, vmax=None, directory='Data', base=None):
    """Plot the given variable for each file from a simulation"""
    global verbose, dpi

    # file_list = get_files(base=base)
    # EDIT: CALL GET_FILES WITH DIRECTORY ARGUMENT
    file_list = get_files(wkdir=directory, base=base)
    file_list = clean_file_list(file_list, varname)

    if verbose > 0:
        print('Found {} files to plot'.format(len(file_list)))

    im, fig = plot_first_figure(file_list, varname, vmin, vmax)
    fig.savefig(varname + '.png', bbox_inches='tight', dpi=200)

    # Draw plots
    def init():
        data = sdf.read(file_list[0], mmap=0)
        plt.title('step={}, time={}'.format(data.Header['step'],
                                            data.Header['time']))
        return im,

    # Draw plots
    def update(filename):
        if verbose > 0:
            print('Generating frame for file {}'.format(filename))
        data = sdf.read(filename, mmap=0)
        var = data.__dict__[varname]
        vdata = var.data.T
        vdata = vdata[:-1, :-1]

        im.set_array(vdata.ravel())
        plt.title('step={}, time={}'.format(data.Header['step'],
                                            data.Header['time']))
        return im,

    ani = animation.FuncAnimation(fig, update, init_func=init,
                                  frames=file_list[::1],
                                  blit=False, interval=1)
    fps = len(file_list) / 8.
    writer = animation.writers['ffmpeg'](fps=fps,
                                         bitrate=5e5,
                                         codec='libx264',
                                         extra_args=['-pix_fmt', 'yuv420p'])
    ani.save(varname + '.mp4', writer=writer, dpi=dpi)
    return ani


def main():
    import argparse
    global verbose, dpi

    verbose = 0
    dpi = 300

    varname = 'Electric_Field_Ey'
    vmin = None
    vmax = None

    parser = argparse.ArgumentParser(description='''
    This generates a movie from a series of SDF files
    ''')
    # parser.add_argument('variable', type=str, default=varname, nargs='?',
    #                     help="Variable to plot")
    # EDIT: TAKE IN MULTIPLE VARIABLES TO PLOT
    parser.add_argument('variable', type=str, default=varname, nargs='*',
                        help="Variable(s) to plot")
    parser.add_argument('-v', '--verbose', action="count", default=0,
                        help="Increase verbosity")
    parser.add_argument('-f', '--filename', type=str, nargs=1,
                        help="Filename for one of the simulation dumps")
    # EDIT: OPTION TO SEND THE DIRECTORY NAME WITH DATA FILES
    parser.add_argument('-d', '--directory', type=str, default='Data', nargs=1,
                        help="Directory for one of the simulation dumps")
    parser.add_argument('-i', '--vmin', type=float, default=vmin, nargs=1,
                        help="Vmin for data display (change min of colorbar)")
    parser.add_argument('-a', '--vmax', type=float, default=vmax, nargs=1,
                        help="Vmax for data display (change max of colorbar)")
    args = parser.parse_args()

    verbose = args.verbose

    if isinstance(args.variable, list):
        var = args.variable[0]
    else:
        var = args.variable
    if isinstance(args.vmin, list):
        vmin = args.vmin[0]
    else:
        vmin = args.vmin
    if isinstance(args.vmax, list):
        vmax = args.vmax[0]
    else:
        vmax = args.vmax

    # plot_figures(args.variable, args.scale, base=args.filename)
    # EDIT: CALL PLOT_FIGURES WITH DIRECTORY ARGUMENT
    # take first element of directory because parser gives args in a list
    plot_figures(var, vmin=vmin, vmax=vmax, directory=args.directory[0],
                 base=args.filename)


if __name__ == "__main__":
    main()
