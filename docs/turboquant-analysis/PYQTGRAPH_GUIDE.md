# PyQtGraph Deep Dive Guide

Comprehensive guide to building high-performance real-time data visualization with PyQtGraph.

## Table of Contents

1. [Why PyQtGraph?](#why-pyqtgraph)
2. [Architecture Overview](#architecture-overview)
3. [Basic Concepts](#basic-concepts)
4. [Performance Optimization](#performance-optimization)
5. [Advanced Features](#advanced-features)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Why PyQtGraph?

### Performance Comparison

| Library | Update Rate (10k points) | CPU Usage | Best For |
|---------|-------------------------|-----------|----------|
| Matplotlib | ~5 FPS | 100% | Static plots, publication |
| PyQtGraph | ~60 FPS | 20% | Real-time, interactive |
| VisPy | ~120 FPS | 15% | GPU-heavy, 3D |
| Dear PyGui | ~60 FPS | 25% | Game-like UIs |

**PyQtGraph advantages:**
- Pure Python (easy to modify)
- Qt integration (native widgets)
- Optimized path rendering
- Built-in analysis tools
- MIT license

---

## Architecture Overview

```
PyQtGraph Application Architecture
===================================

┌─────────────────────────────────────────┐
│           QApplication                  │
│  ┌─────────────────────────────────┐    │
│  │    MainWindow (QMainWindow)     │    │
│  │  ┌─────────────────────────┐    │    │
│  │  │ GraphicsLayoutWidget    │    │    │
│  │  │ ┌─────┐ ┌─────┐ ┌────┐│    │    │
│  │  │ │Plot1│ │Plot2│ │Plot3│    │    │
│  │  │ │ ┌─┐ │ │ ┌─┐ │ │ ┌┐ ││    │    │
│  │  │ │ │C│ │ │ │C│ │ │ │C│││    │    │
│  │  │ │ └─┘ │ │ └─┘ │ │ └┘ ││    │    │
│  │  │ └─────┘ └─────┘ └────┘│    │    │
│  │  └─────────────────────────┘    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

C = Curve (PlotDataItem)
```

---

## Basic Concepts

### 1. The Graphics System

```python
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

# Every PyQtGraph app needs a QApplication
app = QtWidgets.QApplication([])

# GraphicsLayoutWidget holds multiple plots
win = pg.GraphicsLayoutWidget()
win.show()

# Add a plot
plot = win.addPlot()

# Create a curve
curve = plot.plot(pen='y')  # Yellow pen

# Update data
import numpy as np
x = np.arange(1000)
y = np.random.normal(size=1000)
curve.setData(x, y)

# Start event loop
app.exec()
```

### 2. Plot Configuration

```python
# Basic setup
plot = win.addPlot(title="My Plot")
plot.showGrid(x=True, y=True, alpha=0.3)
plot.setLabels(left="Amplitude (mV)", bottom="Time (μs)")
plot.setYRange(-500, 500)
plot.setXRange(0, 100)

# Advanced styling
plot.getAxis('bottom').setStyle(tickFont=pg.QtGui.QFont('Arial', 10))
plot.getViewBox().setMouseMode(pg.ViewBox.PanMode)
plot.setMenuEnabled(False)  # Disable right-click menu
plot.setMouseEnabled(x=True, y=False)  # X-only zoom
```

### 3. Curve Types

```python
# Line plot (default)
curve = plot.plot(pen=pg.mkPen(color='y', width=2))

# Scatter plot
scatter = pg.ScatterPlotItem(
    size=10, 
    pen=pg.mkPen(None), 
    brush=pg.mkBrush(255, 255, 255, 120)
)
plot.addItem(scatter)

# Combined
plot.plot(x, y, pen='y', symbol='o', symbolSize=5)

# Step plot
plot.plot(x, y, stepMode=True, pen='y')
```

### 4. Colors and Pens

```python
# mkPen options
pen = pg.mkPen(
    color=(255, 255, 0),      # RGB
    width=2,                   # Pixel width
    style=QtCore.Qt.DashLine, # Line style
    cosmetic=False             # Scale with view?
)

# Predefined colors
# 'b', 'g', 'r', 'c', 'm', 'y', 'k', 'w'
# Or RGB: (255, 128, 0), hex: '#FF8000'

# Alpha transparency
pen = pg.mkPen((255, 0, 0, 128))  # Semi-transparent red
brush = pg.mkBrush(0, 255, 0, 64)  # Very transparent green
```

---

## Performance Optimization

### 1. Data Update Strategies

**Bad (recreates array every frame):**
```python
def update():
    y = np.random.normal(size=10000)  # New allocation
    curve.setData(y)  # Copy again
```

**Good (pre-allocated buffer):**
```python
# Pre-allocate
buffer = np.zeros(10000)

def update(new_data):
    # Roll buffer
    buffer[:-len(new_data)] = buffer[len(new_data):]
    buffer[-len(new_data):] = new_data
    curve.setData(buffer)  # Zero-copy if same dtype
```

**Better (use deque for streaming):**
```python
from collections import deque

buffer = deque(maxlen=10000)

def update(new_data):
    buffer.extend(new_data)
    curve.setData(np.array(buffer))
```

### 2. Downsample Large Datasets

```python
# Automatic downsampling
curve = plot.plot(downsampleMethod='subsample')
curve.setData(x, y, downsample=10)  # Show every 10th point

# Manual for control
if len(data) > 10000:
    data = data[::len(data)//10000]  # Always show ~10k points
```

### 3. Disable Expensive Features

```python
pg.setConfigOptions(
    useOpenGL=True,          # GPU acceleration
    enableExperimental=True,  # New features
    antialias=False,         # Expensive! Disable for speed
    crashWarning=True        # Debug mode
)

# Per-curve optimization
curve = plot.plot(
    pen=pg.mkPen('y'),
    antialias=False,         # Disable AA per curve
    skipFiniteCheck=True     # Skip NaN/Inf checks
)
```

### 4. Multi-threading

```python
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg

class AcquisitionThread(QThread):
    data_ready = pyqtSignal(np.ndarray)
    
    def run(self):
        while self.running:
            data = acquire_from_hardware()
            self.data_ready.emit(data)
            time.sleep(0.001)

# In main thread
def on_data(data):
    curve.setData(data)  # GUI updates must be in main thread

thread = AcquisitionThread()
thread.data_ready.connect(on_data)
thread.start()
```

### 5. OpenGL Acceleration

```python
# Check if OpenGL is working
print(pg.getConfigOption('useOpenGL'))  # Should be True

# Force software rendering (if GPU issues)
pg.setConfigOption('useOpenGL', False)

# Optimized for OpenGL
pg.setConfigOptions(
    useOpenGL=True,
    enableExperimental=True
)
```

---

## Advanced Features

### 1. Multiple Y-Axes

```python
# Create second Y axis
p1 = win.addPlot()
p2 = pg.ViewBox()
p1.showAxis('right')
p1.scene().addItem(p2)
p1.getAxis('right').linkToView(p2)
p2.setXLink(p1)

# Add curves
curve1 = p1.plot(y1, pen='y')  # Left axis
curve2 = pg.PlotDataItem(y2, pen='r')
p2.addItem(curve2)              # Right axis

# Sync views
def update_views():
    p2.setGeometry(p1.getViewBox().sceneBoundingRect())
p1.getViewBox().sigResized.connect(update_views)
```

### 2. Infinite Lines (Cursors)

```python
# Vertical cursor (time measurement)
cursor_x = pg.InfiniteLine(
    angle=90,              # Vertical
    movable=True,          # Draggable
    pen=pg.mkPen('y', style=QtCore.Qt.DashLine)
)
plot.addItem(cursor_x)

# Horizontal cursor (level measurement)
cursor_y = pg.InfiniteLine(angle=0, movable=True, pen='c')
plot.addItem(cursor_y)

# Cursor value callback
def on_cursor_moved(line):
    print(f"Cursor at: {line.value()}")
cursor_x.sigPositionChanged.connect(on_cursor_moved)
```

### 3. Linear Region Item (Selection)

```python
region = pg.LinearRegionItem(
    values=[20, 40],       # Initial position
    orientation='vertical' # Time selection
)
region.setBrush(pg.mkBrush(255, 255, 255, 50))
plot.addItem(region)

# Get selected range
def on_region_changed():
    min_x, max_x = region.getRegion()
    print(f"Selected: {min_x} to {max_x}")
region.sigRegionChanged.connect(on_region_changed)
```

### 4. ROI (Region of Interest)

```python
roi = pg.RectROI(
    [20, 20],              # Position
    [20, 20],              # Size
    pen='r',
    rotatable=True,
    resizable=True
)
plot.addItem(roi)

# Get selected data
def on_roi_changed():
    region = roi.getArrayRegion(data, image_item)
    print(f"Mean in ROI: {np.mean(region)}")
roi.sigRegionChanged.connect(on_roi_changed)
```

### 5. Color Maps and Images

```python
# Create color map
cmap = pg.ColorMap(
    pos=[0, 0.5, 1],
    color=[(0, 0, 0), (128, 0, 128), (255, 255, 0)]
)

# Apply to image
img = pg.ImageItem(image_data)
img.setLookupTable(cmap.getLookupTable())
plot.addItem(img)

# Or use preset
img.setColorMap(pg.colormap.get('viridis'))
```

### 6. Layout Management

```python
# Grid layout
win = pg.GraphicsLayoutWidget()
win.setWindowTitle('Grid Layout')

# Row 0
p1 = win.addPlot(row=0, col=0)
p2 = win.addPlot(row=0, col=1)

# Row 1 (spans 2 columns)
p3 = win.addPlot(row=1, col=0, colspan=2)

# Next row
win.nextRow()
p4 = win.addPlot()

# Linked axes
p2.setXLink(p1)
p3.setYLink(p1)
```

---

## Common Patterns

### Pattern 1: Oscilloscope Display

```python
class Oscilloscope:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.win = pg.GraphicsLayoutWidget()
        self.plot = self.win.addPlot()
        
        # Setup
        self.plot.showGrid(x=True, y=True)
        self.plot.setYRange(-5, 5)
        
        # Trigger line
        self.trigger_line = pg.InfiniteLine(angle=0, movable=True)
        self.plot.addItem(self.trigger_line)
        
        # Curves
        self.curves = []
        for i, color in enumerate(['y', 'c', 'm', 'g']):
            curve = self.plot.plot(pen=color)
            self.curves.append(curve)
        
        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
        
    def update(self):
        for curve in self.curves:
            data = np.random.normal(size=1000)
            curve.setData(data)
```

### Pattern 2: Waterfall/Spectrogram

```python
class WaterfallDisplay:
    def __init__(self):
        self.history = deque(maxlen=100)
        self.img = pg.ImageItem()
        self.plot.addItem(self.img)
        
    def update(self, spectrum):
        self.history.append(spectrum)
        # Convert to 2D array
        data = np.array(self.history)
        self.img.setImage(data.T)
```

### Pattern 3: Rolling Time Series

```python
class RollingPlot:
    def __init__(self, buffer_size=10000):
        self.buffer = np.zeros(buffer_size)
        self.ptr = 0
        
    def add_data(self, new_data):
        n = len(new_data)
        if self.ptr + n < len(self.buffer):
            self.buffer[self.ptr:self.ptr+n] = new_data
            self.curve.setData(self.buffer[:self.ptr+n])
        else:
            # Roll buffer
            self.buffer[:-n] = self.buffer[n:]
            self.buffer[-n:] = new_data
            self.curve.setData(self.buffer)
```

---

## Troubleshooting

### Issue: Slow Performance

**Symptoms:** Low FPS, laggy UI

**Solutions:**
1. Check `antialias` is False
2. Use OpenGL: `pg.setConfigOption('useOpenGL', True)`
3. Downsample: `curve.setData(data, downsample=10)`
4. Profile: Use `cProfile` to find bottlenecks

### Issue: Memory Leaks

**Symptoms:** Memory grows over time

**Solutions:**
1. Don't create new arrays every frame
2. Use `curve.setData()` instead of `plot.plot()` repeatedly
3. Clear unused items: `plot.removeItem(item)`

### Issue: OpenGL Not Working

**Symptoms:** Black screen or artifacts

**Solutions:**
1. Check graphics drivers
2. Force software: `pg.setConfigOption('useOpenGL', False)`
3. Update PyQt5/PyQtGraph

### Issue: Threading Errors

**Symptoms:** "QObject::setParent: Cannot set parent" or crashes

**Solutions:**
1. All GUI updates must be in main thread
2. Use signals/slots: `data_ready.emit(data)`
3. Don't touch Qt objects from worker threads

---

## Best Practices

1. **Pre-allocate buffers** - Avoid dynamic allocation in update loops
2. **Use same dtype** - `setData()` is zero-copy if dtype matches
3. **Batch updates** - Process multiple points before redrawing
4. **Profile first** - Don't optimize blindly; measure
5. **Separate concerns** - Acquisition thread ≠ GUI thread
6. **Handle NaN/Inf** - Use `np.nan_to_num()` if data can have gaps

---

## Resources

- **Official docs:** https://pyqtgraph.readthedocs.io/
- **GitHub:** https://github.com/pyqtgraph/pyqtgraph
- **Examples:** Run `python -m pyqtgraph.examples`
- **Community:** r/pyqtgraph on Reddit

---

## Quick Reference Card

```python
# Imports
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import numpy as np

# Config (do this first!)
pg.setConfigOptions(
    useOpenGL=True,
    antialias=False
)

# App setup
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget()
win.show()

# Plot
plot = win.addPlot(title="Plot")
plot.showGrid(x=True, y=True)
plot.setYRange(-1, 1)

# Curve
curve = plot.plot(pen=pg.mkPen('y', width=2))

# Update
def update():
    data = np.random.normal(size=1000)
    curve.setData(data)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(16)

# Run
app.exec()
```
