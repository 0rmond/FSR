import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import curve_fit


def lorentzian(x, offset, centre, width, area):
    shape = ((2*area*np.pi)
             * width
             / (4 * ((x - centre)**2) + (width**2))
             )
    return offset - shape

def label_distance(point1, point2):
    x_position = point1 + (point2 - point1)/2
    label = f"{round((point2-point1)*1e3, 3)}ms"
    return x_position, label

def draw_arrow(axes, point1, point2, ypos, width):
    """<-- -->
    """
    midpoint = point1 + (point2 - point1)/2
    left_arrow = axes.arrow(midpoint, ypos, -width/2, 0, linewidth=1, color="black", head_width=0.2*width)
    right_arrow = axes.arrow(midpoint, ypos, width/2, 0, linewidth=1, color="black", head_width=0.5*width)

    return left_arrow, right_arrow

def label_lorentz_width(a, point1, point2):

    x_pos, label = label_distance(point1, point2)

    bbox=dict(fc="white", ec="none")
    centre_y = 0.5*abs(a.get_ylim()[1] - a.get_ylim()[0]) + a.get_ylim()[0]

    a.text(x=x_pos, y=centre_y, s=label, ha="center", va="center", bbox=bbox, fontsize=12)

plt.style.use('ormstyle.mplstyle')

data = []
headers = ["Channel B (Input 2) (V)"]

f, a = plt.subplots()

slice_range = (0.0067, 0.08)
slice_range = (0.025, 0.135)

file = "Data/first_fsr_measurement.csv"
file = "Data/second_fsr_measurement.csv"
df = pd.read_csv(file, comment="%", names=headers, index_col=0)
df.index.name = "Time (s)"

sliced_df = df.loc[slice_range[0]:slice_range[1]]
trough_locations = find_peaks(sliced_df[headers[0]] * -1, distance=150)[0]
a.plot(sliced_df.index, sliced_df[headers[0]])

trough_df = sliced_df.iloc[trough_locations]
mean_dt = np.array(trough_df.index.diff().values[1:]).mean()

fit_ranges = [[trough - (mean_dt/2), trough + (mean_dt/2)] for trough in trough_df.index]





fit_dfs = [sliced_df.loc[fit_range[0]: fit_range[1]] for fit_range in fit_ranges]

widths = []
for fit_df, col, trough_time in zip(fit_dfs, ["tab:red", "tab:orange", "tab:pink"], trough_df.index):


    ydata = fit_df[headers[0]]
    lorentz_fit, _ = curve_fit(lorentzian, fit_df.index, ydata, p0=(max(ydata), trough_time, 1, 1))
    width = lorentz_fit[-1]
    lorentz_xdata = np.linspace(fit_df.index[0], fit_df.index[-1], 1000)
    lorentz_ydata = lorentzian(lorentz_xdata, *lorentz_fit)

    a.plot(fit_df.index, fit_df[headers[0]], color="black", marker='x', linewidth=0)
    a.plot(lorentz_xdata, lorentz_ydata, color=col, linewidth=4)

    points = [lorentz_fit[1] - width/2, lorentz_fit[1] + width/2]
    label_lorentz_width(a, *points)
    widths.append(width)

a.plot(trough_df.index, trough_df[headers[0]], marker='x', color="red", linewidth=0)
finesse = mean_dt / np.array(widths).mean()
a.set_xlabel("Time (s)")
a.set_ylabel("Voltage (V)")
a.set_title(f"Finesse: {finesse}")
plt.show()
