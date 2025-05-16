# GEOframePy

![PyPI](https://img.shields.io/pypi/v/geoframepy)
![License](https://img.shields.io/pypi/l/geoframepy)

**GEOframePy** is a Python library that supports hydrological modeling using the [GEOframe-NewAGE](http://geoframe.blogspot.com/) system. It offers tools for data preprocessing, model configuration, and results analysis within a Pythonic framework.

---

## 🧭 Table of Contents

- [🌐 About](#-about)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [🔧 Features](#-features)
- [📂 Module Reference](#-module-reference)
- [🧪 Testing](#-testing)
- [🤝 Contributing](#-contributing)
- [📞 Contact & Support](#-contact--support)
- [📜 License](#-license)
- [🔗 Useful Links](#-useful-links)

---

## 🌐 About

GEOframePy provides Python interfaces and utilities for setting up and analyzing simulations using the GEOframe modeling environment. It supports preprocessing for input data (e.g., shapefiles, timeseries), topology analysis, and I/O for OMS-formatted files.

Explore the full GEOframe ecosystem on the [official blog](http://geoframe.blogspot.com/).

---

## 📦 Installation

Install the latest version via pip:

```bash
pip install geoframepy
```

---

## 🚀 Quick Start

After installation, you can begin using the library. Here's a simple example:

```python
from topology.network import get_raw_network

net = get_raw_network('path/to/topology.txt')
```

---

## 🔧 Features

- 🌍 **Hydrological Modeling Support**
- 📈 **Time Series Import/Export (OMS Format)**
- 🗺️ **Subbasin Shapefile Management**
- 🔄 **Network Topology Parsing and Simplification**
- 🧪 **Centroid Consistency Checking**
- 📊 **Output CSV Generation for Subbasin Nodes**

---

## 📂 Module Reference

### `subbasins_check/geoframe_polygons.py`
- `clone_shape_file()`: Clones shapefile and related files.
- `check_centroid()`: Validates centroid position, optionally adjusts.

### `timeseries/file_utils.py`
- `process_network_to_timeseries()`: Generates and saves timeseries per subbasin.

### `timeseries/io_csv.py`
- `pandas_read_OMS_timeseries()`: Reads OMS-formatted timeseries.
- `write_OMS_timeseries()`: Exports DataFrame to OMS-compliant CSV.

### `topology/network.py`
Handles network topology:
- `get_raw_network()`
- `get_network()`
- `check_network()`
- `filter_to_calibrate()`
- `get_up_streem_network()`
- `get_subgraph()`
- `get_downstream_network()`
- `create_stream_gauge_dictionary()`
- `write_network()`
- `sort_node()`
- `get_order_node()`
- `simplify_network()`


## ⚙️ OMS Module (`oms_module/oms.py`)

This module provides cross-platform support for running OMS3 simulations via Python.

### Features

- 🔍 **Automatic Java JDK 11 Detection** for Windows, macOS, and Linux
- 📁 **OMS Project Setup**: Validate paths and prepare console environment
- ▶️ **Simulation Runner**: Execute `.sim` files using the `oms3.CLI` interface
- 🧾 **Logging System**: Stores info, warnings, errors, and execution history
- 🧼 **Cleanup Tools**: Reset environment and logs
- 🛠️ **Diagnostics**: Identify common issues such as missing folders or incorrect Java versions

### Example Usage

```python
from oms_module.oms import setup_OMS_project, run_simulation, show_logs

setup_OMS_project(
    java_path="/usr/lib/jvm/java-11-openjdk-amd64/bin/java",
    proj_location="/path/to/project",
    console_location="/path/to/oms-console"
)

run_simulation("simulation/sim_file.sim")

show_logs()
```

> ℹ️ For more advanced control (e.g., capturing logs, debugging simulation failures, diagnosing Java issues), refer to the function docstrings inside `oms.py`.
---

## 🧪 Testing

Run the test suite using:

```bash
pytest
```

Make sure dependencies are installed and the Python environment is activated.

---

## 🤝 Contributing

We welcome contributions from the community! To contribute:

1. 🍴 Fork the repository
2. 🌿 Create a new branch
3. ✍️ Implement your changes
4. ✅ Run tests
5. 📩 Submit a pull request

---

## 📞 Contact & Support

- 🐞 Report issues at: [GitHub Issues](https://github.com/geoframecomponents/GEOframePy/issues)
- 💬 Developer mailing list: [geoframe-components-developers](https://groups.google.com/u/1/g/geoframe-components-developers?pli=1)
- 📚 User/educational list: [geoframe-schools](https://groups.google.com/u/0/g/geoframe-schools)

---

## 📜 License

Licensed under the [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.en.html).

---

## 🔗 Useful Links

- 🌍 [GEOframe Blog](http://geoframe.blogspot.com/)
- 💻 [geoframecomponents GitHub](https://github.com/geoframecomponents)
- 📦 [GEOframe OMS Projects](https://github.com/GEOframeOMSProjects)
