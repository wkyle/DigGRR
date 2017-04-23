#!/usr/bin/env python3

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
import numpy as np

fig = Figure(figsize=(10,10), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvas(fig)


x = np.linspace(0,10,100)
y = np.sin(4*x)

ax.plot(x,y)
ax.text(5, .5, r'$\frac{1}{\alpha}mm$', fontsize=22, usetex=True)

fig.savefig('textest.pdf')
