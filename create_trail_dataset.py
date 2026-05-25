import osmium
import shapely.wkb
from shapely.geometry import LineString, MultiLineString
from shapely.strtree import STRtree


class TrailRoute:

    def __init__(self, relation_id, node_ids):
        self.relation_id = relation_id
        self.node_ids = node_ids


class AreaConstructor(osmium.SimpleHandler):
    def __init__(self, admin_levels=(2, 4, 6, 7, 8, 10)):
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
        self.relation_ids: dict[int, list] = {}

    def relation(self, r):
        if r.tags.get('route') == 'hiking':
            self.relation_ids[r.id] = []
            for member in r.members:
                if member.type == 'w':
                    self.relation_ids[r.id].append(member.ref)


class NodesPerWayConstructor(osmium.SimpleHandler):

    def __init__(self, way_ids: set[int]):
        super().__init__()
        self.way_ids = way_ids
        self.nodes_per_way: dict[int, list] = {}

    def way(self, w):
        if w.id in self.way_ids:
            self.nodes_per_way[w.id] = [(n.lon, n.lat) for n in w.nodes]


area_constructor = AreaConstructor()
area_constructor.apply_file('greece-260524.osm.pbf', locations=True)

relation_to_way_constructor = RelationToWayConstructor()
relation_to_way_constructor.apply_file('greece-260524.osm.pbf')

nodes_per_way_constructor = NodesPerWayConstructor(
    way_ids=set([way for ways in relation_to_way_constructor.relation_ids.values() for way in ways])
)
nodes_per_way_constructor.apply_file('greece-260524.osm.pbf', locations=True)

trails = []
for relation_id, way_ids in relation_to_way_constructor.relation_ids.items():
    lines = [
        LineString(nodes_per_way_constructor.nodes_per_way[wid])
        for wid in way_ids
        if wid in nodes_per_way_constructor.nodes_per_way and len(nodes_per_way_constructor.nodes_per_way[wid]) >= 2
    ]
    if lines:
        trails.append({
            'id': relation_id,
            'geometry': MultiLineString(lines),
            'names': [],  # admin_level -> list of names
        })

boundary_geoms = [b['geometry'] for b in area_constructor.boundaries]
tree = STRtree(boundary_geoms)

for trail in trails:
    indexes = tree.query(trail['geometry'], predicate='intersects')
    for i in indexes:
        b = area_constructor.boundaries[i]
        trail['names'].append(b['name'])

print(1)
