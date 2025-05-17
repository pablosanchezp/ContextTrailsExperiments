# Context-Aware Postfiltering Algorithms

## Requirements

- Python >= 3.10
- [Ranx](https://github.com/AmenRa/ranx)

## 1. Folder Structure

Before running the scripts, create the following folder structure:

```
data/
├── raw/
│ └── {dataset}/
│ ├── {dataset}mapped_trails_weather_aggregated_Temp80train.csv
│ ├── {dataset}mapped_trails_weather_aggregated_Temp20test.csv
│ ├── POIS{dataset}.csv
│ ├── POIS_INFO{dataset}.csv
│ └── weather/
├── cleaned/
└── predictions/
```

> Replace `{dataset}` with the name of the city dataset.

## 2. Run the Scripts

Follow these steps in order:

```bash
python prepare_data_cars.py
python full_experiment.py
python evaluate_cars.py
```
