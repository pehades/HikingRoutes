import json

import osmium
import shapely.wkb
from shapely.geometry import MultiLineString
from shapely.strtree import STRtree

from geometry import get_elevation, haversine
from hiking_routes.models import TrailDb


class TrailRoute:

    def __init__(self, relation_id, node_ids):
        self.relation_id = relation_id
        self.node_ids = node_ids


class AreaConstructor(osmium.SimpleHandler):
    def __init__(self, admin_levels=(4, 5)):
        super().__init__()
        self.admin_levels = set(admin_levels)
        self.wkbfab = osmium.geom.WKBFactory()
        self.boundaries: list[dict] = []

    def area(self, a):
        boundary = a.tags.get('boundary')

        if boundary in {'protected_area', 'national_park'}:
            extra = {'kind': boundary}
        elif boundary == 'administrative':
            try:
                level = int(a.tags.get('admin_level', ''))
            except ValueError:
                return
            if level not in self.admin_levels:
                return
            extra = {'kind': 'admin', 'admin_level': level}
        else:
            return

        name = a.tags.get('name')
        if not name:
            return
        try:
            wkb = self.wkbfab.create_multipolygon(a)
        except Exception:
            return

        self.boundaries.append({
            'name': name,
            'geometry': shapely.wkb.loads(bytes.fromhex(wkb)),
            **extra,
        })


class RelationToWayConstructor(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.relation_info: dict = {}

    def relation(self, r):
        if r.tags.get('route') == 'hiking':
            self.relation_info[r.id] = {
                'name': r.tags.get('name'),
                'ways': []
            }
            for member in r.members:
                if member.type == 'w':
                    self.relation_info[r.id]['ways'].append(member.ref)


class NodesPerWayConstructor(osmium.SimpleHandler):

    def __init__(self, way_ids: set[int]):
        super().__init__()
        self.way_ids = way_ids
        self.nodes_per_way: dict[int, list] = {}

    def way(self, w):
        if w.id in self.way_ids:
            self.nodes_per_way[w.id] = [{'lon': n.lon, 'lat': n.lat} for n in w.nodes]


area_constructor = AreaConstructor()
area_constructor.apply_file('greece-260524.osm.pbf', locations=True)

relation_to_way_constructor = RelationToWayConstructor()
relation_to_way_constructor.apply_file('greece-260524.osm.pbf')

nodes_per_way_constructor = NodesPerWayConstructor(
    way_ids=set(
        [way
         for relation_id in relation_to_way_constructor.relation_info.keys()
         for way in relation_to_way_constructor.relation_info[relation_id]['ways']]
    )
)
nodes_per_way_constructor.apply_file('greece-260524.osm.pbf', locations=True)

trails = []

for relation_id, relation_info in relation_to_way_constructor.relation_info.items():
    lines = [
        nodes_per_way_constructor.nodes_per_way[wid]
        for wid in relation_info['ways']
        if wid in nodes_per_way_constructor.nodes_per_way and len(nodes_per_way_constructor.nodes_per_way[wid]) >= 2
    ]
    if lines:
        coordinates = [coordinate for line in lines for coordinate in line]
        geometry = [
            [[coordinate['lon'], coordinate['lat']] for coordinate in line] for line in lines
        ]
        elevation_profile = get_elevation(coordinates)
        ascend = sum([max(0, elevation_profile[i] - elevation_profile[i-1]) for i in range(1, len(elevation_profile))])
        descend = sum([min(0, elevation_profile[i] - elevation_profile[i-1]) for i in range(1, len(elevation_profile))])

        trail_length = haversine(coordinates)

        trails.append({
            'id': relation_id,
            'name': relation_info['name'],
            'start_point': coordinates[0],
            'end_point': coordinates[-1],
            'coordinates': coordinates,
            'length': trail_length,
            'elevation_profile': elevation_profile,
            'ascend': ascend,
            'descend': descend,
            'geometry': MultiLineString(geometry),
            'description': [],
        })

boundary_geoms = [b['geometry'] for b in area_constructor.boundaries]
tree = STRtree(boundary_geoms)

for trail in trails:
    indexes = tree.query(trail['geometry'], predicate='intersects')
    for i in indexes:
        b = area_constructor.boundaries[i]
        trail['description'].append(b['name'])

trails_processed = []
for trail in trails:
    if trail['name'] is None or trail['name'] == '':
        continue
    trail.pop('geometry')
    trail['description'] = ' '.join(trail['description'])

    trails_processed.append(trail)



with open('trails.json', 'w') as f:
    f.write(json.dumps(trails_processed))
print(1)
