#!/usr/bin/python3

from gi.repository import Gtk, Gdk, GLib
import numpy as np

filename = 'TEST_x_y_dx_dy.dat'


f = np.loadtxt(filename, unpack=True)

print(len(f))
