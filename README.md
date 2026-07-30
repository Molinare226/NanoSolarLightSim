# NanoSolarLightSim

A UE5-based solar light simulation framework for analysing solar exposure of smart solar benches under different sun positions and times.

## Overview

This project uses Unreal Engine 5 to create a digital twin simulation environment for solar energy analysis.

The system can:

- Convert GPS coordinates into Unreal Engine world coordinates
- Automatically place solar bench assets
- Generate observation cameras
- Simulate different sunlight conditions
- Render image sequences for analysis


## Features

### Geographic Placement

The project integrates UE GeoReferencing System.

Input:

- Latitude
- Longitude


Example:


Latitude: -33.889847
Longitude: 151.191894



### Automated Simulation Pipeline


GPS Location
|
v
Geo Referencing
|
v
Object Placement
|
v
Camera Generation
|
v
Solar Simulation
|
v
Rendered Output



## Requirements

- Unreal Engine 5.8
- Python Editor Scripting Plugin
- GeoReferencing Plugin


## Usage

Run the Python script in the logPython of UE:

```python
import testFirst as tsf 
tsf.run_all(
    -33.889847,
    151.191894
)
```

## The system will automatically:

Spawn the solar bench
Detect ground height
Create a camera
Generate a sequence
Render the simulation
Future Work
Full-day solar simulation
Solar radiation estimation
Photovoltaic performance prediction
Weather data integration


## Author

Xieyu Huang
University of Sydney
