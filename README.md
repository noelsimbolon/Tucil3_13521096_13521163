## Overview

This is a Python implementation for finding the closest path using the Uniform Cost Search (UCS) and A* (A-star) algorithms, packaged in a desktop app.

The program can accept input from a text file or from user-defined markers and paths on the integrated map.

After clicking <kbd>Start</kbd>, the program finds the shortest route using either the UCS or A* algorithm.

Once the path-finding is complete, the program displays the route, its distance, and a visualization of the path.

[![compass.png](https://i.postimg.cc/26Nd4c5x/compass.png)](https://postimg.cc/WDSJV7gD)
[![compass-hollywood.png](https://i.postimg.cc/2yNDNBxw/compass-hollywood.png)](https://postimg.cc/PpycmJ9p)

## Prerequisites

- [Python 3.11.2](https://www.python.org/downloads/release/python-3112/)
- Required packages as specified
  in [`requirements.txt`](https://github.com/noelsimbolon/Tucil3_13521096_13521163/blob/main/requirements.txt)

## Directory Structure

```
├── doc        # Contains report for the project
├── resources  # Contains example input files
├── src        # Contains source code for the program
...
```

## How To Use

1. Download this repository as a ZIP file and extract it to a directory somewhere
2. Open your terminal and navigate to said directory
3. Activate the virtual environment in which you want to install packages
4. Install required packages using `pip`

   ```shell
   pip install -r requirements.txt
   ```
5. Run the app using `python` from the root directory

    ```shell
    python -m src.compass
    ```
   
### Input from File

1. Click <kbd>Open File</kbd> to open a text file as an input for the program\
   See [resouces](https://github.com/noelsimbolon/Tucil3_13521096_13521163/blob/main/resources/) for valid example
   of input files. Below is a brief explanation of the structure of the input file.
   
   ```txt
   8                  ─ # The number of nodes
   8 22               ┐
   0 3                │
   2 3                │
   5 7                ├ # These are coordinates for the nodes
   3 5                │
   4 8                │
   8 0                │
   6 9                ┘
   0 2 3 0 0 0 0 0    ┐
   2 0 0 4 0 0 0 0    │
   3 3 0 0 5 0 0 0    │
   0 4 5 0 6 0 0 0    ├ # This is the weighted adjacency matrix
   0 0 0 6 0 7 0 0    ├ # The weight represents the distance between nodes
   0 0 0 0 7 0 8 0    │
   0 0 0 0 0 8 0 9    │
   0 0 0 0 0 0 9 0    ┘
   ```
2. Enter the starting node and the destination node
3. Choose a path-finding algorithm (default is A*)
4. Click <kbd>Start</kbd> to initiate the path-finding process

### Input from Map

1. Add markers on the map by right-clicking on it and selecting <kbd>Add Marker</kbd> from the context menu
2. Add paths on the map by entering the marker numbers you want to connect and clicking <kbd>Add Path</kbd>
3. Select the starting node and the destination node by entering their respective marker numbers
4. Choose a path-finding algorithm (default is A*)
5. Click <kbd>Start</kbd> to initiate the path-finding process

## Author

| Name               | GitHub                                          |
|--------------------|-------------------------------------------------|
| Noel Simbolon      | [noelsimbolon](https://github.com/noelsimbolon) |
| Zidane Firzatullah | [zidane-itb](https://github.com/zidane-itb)     |
