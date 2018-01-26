# vacuum-analysis.py
#
# Analysis for vacuum lab in Phys 4007
# David Lister
# January 2018
#

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import glob
import datetime as dt

FILES = 'data/*'

def pressure_analysis(fname):
    time_col = 0
    pressure_col = 1
    s_per_sample = float(input("How many seconds per sample?: "))
    sample_to_s = lambda t: s_per_sample * t
    mB_to_torr = lambda x: 0.750062 * x
    data = pd.read_csv(fname, sep='\t')
    time_header = list(data)[time_col]
    pressure_header = list(data)[pressure_col]
    data[time_header] = data[time_header].apply(sample_to_s)
    data[pressure_header] = data[pressure_header].apply(mB_to_torr)
    time = np.array(data[time_header])
    pressure = np.array(data[pressure_header])
    plt.semilogy(time, pressure)
    plt.show()

    t_start = float(input("Start fit at: "))
    t_end = float(input("End fit at: "))
    pressure_ln = np.log(pressure)
    mask = (time>t_start) * (time<t_end)
    slope, intercept, r_value, p_value, std_err = stats.linregress(time[mask], pressure_ln[mask])

    fit_ln = time * slope + intercept
    fit = np.exp(fit_ln)
    print(slope, intercept, r_value, p_value, std_err)
    title = input("Title: ")
    xaxis = input("X-label: ")
    yaxis = input("Y-label: ")
    plt.semilogy(time, pressure)
    plt.semilogy(time, fit, "-")
    plt.title(title)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.show()

def bulk_pressure(fname):
    files = glob.glob(fname + "/*")
    time_col = 0
    pressure_col = 1
    s_per_sample = float(input("How many seconds per sample?: "))
    sample_to_s = lambda t: s_per_sample * t
    mB_to_torr = lambda x: 0.750062 * x
    legend = []
    for file in files:
        legend.append(file.split("\\")[-1])
        data = pd.read_csv(file, sep='\t')
        time_header = list(data)[time_col]
        pressure_header = list(data)[pressure_col]
        data[time_header] = data[time_header].apply(sample_to_s)
        data[pressure_header] = data[pressure_header].apply(mB_to_torr)
        time = np.array(data[time_header])
        pressure = np.array(data[pressure_header])
        plt.semilogy(time, pressure, label=legend[-1])
    plt.legend(legend)
    plt.title("ln(Pressure) vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("ln(Pressure)")
    plt.show()

def rga_analysis(fname):
    files = glob.glob(fname+ "/*")
    data = []
    times = {}
    i = 0
    for file in files:
        spectra = pd.read_csv(file, header=18)
        spectra = spectra.values
        spectra = spectra.transpose()
        spectra = spectra[:2]
        f = open(file)
        line = f.readline()
        time = dt.datetime.strptime(line, '%b %d, %Y  %I:%M:%S %p\n')
        data.append([time.timestamp(), spectra])
        times[time.timestamp()] = i
        i += 1
    order = list(times.keys())
    order.sort()
    print(order)
    time_series = np.array([data[times[time]][1][1] for time in order])
    weight = data[0][1][0]
    time = np.array(order) - min(order)
    print(time_series.shape)
    print(time.shape)
    print(weight.shape)
    delta_spectra = np.array([time_series[i+1] - time_series[i] for i in range(len(time_series) - 1)])
    delta_time = np.array([time[i+1] - time[i] for i in range(len(time) - 1)])
    speed = np.array([delta_spectra[i]/delta_time[i] for i in range(len(delta_time))])
    average_speed = np.array([np.mean(row) for row in speed.transpose()])
    average_speed.transpose()
    print(average_speed.shape)
    plt.plot(weight, average_speed)
    plt.show()







if __name__ == "__main__":
    flist = glob.glob(FILES)

    i = 0
    for f in flist:
        print(i, f)
        i += 1

    findex = int(input('Enter the number for the file you want to analyze: '))

    atype = int(input("Enter 1 for pressure analysis, 2 for RGA analysis and 3 for outgas: "))

    if atype == 1:
        pressure_analysis(flist[findex])

    elif atype == 2:
        rga_analysis(flist[findex])

    elif atype == 3:
        bulk_pressure(flist[findex])

    else:
        print("Invalid entry")