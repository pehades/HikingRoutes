import numpy as np
import srtm

from hiking_routes.models import Coordinate

srtm_data = srtm.get_data()


def haversine(coordinates: list[dict]) -> float:

    coordinates = np.array([[coordinate['lon'], coordinate['lat']] for coordinate in coordinates])
    """
    Compute pairwise haversine distances between consecutive points.

    coordinates: (N, 2) array of [lon, lat] in degrees
    returns: (N-1,) array of distances in kilometers
    """
    R = 6_371_000  # Earth radius in meters

    lon, lat = np.radians(coordinates[:, 0]), np.radians(coordinates[:, 1])

    dlat = np.diff(lat)
    dlon = np.diff(lon)

    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:-1]) * np.cos(lat[1:]) * np.sin(dlon / 2) ** 2

    return float((2 * R * np.arcsin(np.sqrt(a)) / 1000).sum().round(1))


def get_elevation(coordinates: list[dict]):
    elevation = [
        srtm_data.get_elevation(coordinate['lon'], coordinate['lat'])
        for coordinate in coordinates
    ]
    return [v for v in elevation if v is not None]
