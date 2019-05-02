import pandas as pd
import folium
import collections
from branca.colormap import linear
from h3 import h3
from fastkml import kml
from shapely_geojson import dumps, Feature, FeatureCollection
from shapely.geometry import LinearRing, Polygon, MultiPolygon, Point


def geometry_to_coords(shape):
    if type(shape) == LinearRing:
        return [[i[0], i[1]] for i in shape.coords]
    elif type(shape) == Polygon:
        return [[i[0], i[1]] for i in shape.exterior.coords]
    else:
        return None


def read_kml_to_shapely(kml_file):
    with open(kml_file, 'rt', encoding='utf-8') as myfile:
        doc = myfile.read().encode('utf-8')
    k = kml.KML()
    k.from_string(doc)
    features = list(k.features())
    features_list = list(features[0].features())
    polygon_df = pd.DataFrame()
    for shape in features_list:
        try:
            polygon_df = polygon_df.append({'name': shape.name, 'polygon': shape.geometry}, ignore_index=True)
        except:
            pass
    polygon_df['clean_polygon'] = polygon_df['polygon'].map(geometry_to_coords)
    return polygon_df


def reverse_lat_lng_order(shape):
    if type(shape) == MultiPolygon:
        return MultiPolygon(
            [Polygon([[j[1], j[0]] for j in list(polygon.exterior.coords)]).buffer(0) for polygon in shape])
    else:
        return Polygon([[i[1], i[0]] for i in list(shape.exterior.coords)]).buffer(0)


class h3folium(object):
    def __init__(self, center=(0, 0), zoom_start=12):
        self.map = folium.Map(center, zoom_start=zoom_start)

    def points_to_h3_map(self, coord_list, res, color_palette='YlOrRd_09', weight=1, fillOpacity=0.7, color='black',
                         labels=True, sticky=True):
        h3_list = [h3.geo_to_h3(c[0], c[1], res) for c in coord_list]
        h3_count_dict = collections.Counter(h3_list)
        color_dict = {}
        color_map = getattr(linear, color_palette).scale(min(h3_count_dict.values()),
                                                         max(h3_count_dict.values()))
        for key in h3_count_dict.keys():
            color_dict[key] = color_map(h3_count_dict[key])
        features = [
            Feature(Polygon([[j[1], j[0]] for j in h3.h3_to_geo_boundary(h)]), {'id': h, 'count': h3_count_dict[h]})
            for h in h3_count_dict.keys()]
        hexagon_json = dumps(FeatureCollection(features))
        draw = folium.GeoJson(
            hexagon_json, style_function=lambda feature: {
                'fillColor': color_dict[feature['properties']['id']],
                'color': color,
                'weight': weight,
                'fillOpacity': fillOpacity
            }, tooltip=folium.features.GeoJsonTooltip(fields=['id', 'count'],
                                                      labels=labels,
                                                      sticky=sticky,
                                                      ))
        self.map.add_child(draw)
        self.map.add_child(folium.map.LayerControl())
        return self.map

    def polygons_to_h3_map(self, shape, res, reset_center=False, fill_color='Orange', color='black', weight=1,
                           dash_array='5, 5', fill_opacity=0.7, labels=True, sticky=True):
        if reset_center:
            if type(shape) == Polygon:
                shape = [shape]
            self.map.location = list(shape[0].exterior.coords)[0]
        for polygon in shape:
            h3_list = list(h3.polyfill(eval(dumps(polygon)), res))
            if not h3_list:
                features = [Feature(Polygon([[j[1], j[0]] for j in h3.h3_to_geo_boundary(i)]), {'id': i}) for i in
                            h3_list]
                feature_collection = FeatureCollection(features)
                polygon_json = dumps(feature_collection)
                draw = folium.GeoJson(
                    polygon_json,
                    style_function=lambda feature: {
                        'fillColor': fill_color,
                        'color': color,
                        'weight': weight,
                        'dashArray': dash_array,
                        'fillOpacity': fill_opacity,
                    }, tooltip=folium.features.GeoJsonTooltip(fields=['id'],
                                                              labels=labels,
                                                              sticky=sticky,
                                                              ))
                self.map.add_child(draw)
        return self.map

    def polygon_group_to_h3_map(self, data, shape_column, res, group_column, reset_center=False,
                                color_palette='Set1_09', show_first_only=True, color='black', weight=1, dash_array=None,
                                fill_opacity=0.7,labels=True,sticky=True):
        if reset_center:
            first_shape = data[shape_column][0]
            if type(data[shape_column][0]) == Polygon:
                first_shape = [first_shape]
            self.map.location = list(first_shape[0].exterior.coords)[0]
        show = True
        color_dict = {}
        group_dict = {v: k for k, v in enumerate(data[group_column].unique())}
        color_map = getattr(linear, color_palette).scale(min(group_dict.values()), max(group_dict.values()))
        for k in group_dict.keys():
            color_dict[k] = color_map(color_map[k])
        for key, value in group_dict.items():
            if show_first_only and value:
                show = False
            feature_group = folium.map.FeatureGroup(name=key, show=show)
            h3_list = []
            rows = data[data[group_column] == key]
            for _, row in rows.iterrows():
                h3_list += list(h3.polyfill(eval(dumps(row[shape_column])), res))
            h3_list = list(set(h3_list))
            features = [Feature(Polygon([[j[1], j[0]] for j in h3.h3_to_geo_boundary(i)]), {'id': i}) for i in
                        h3_list]
            feature_collection = FeatureCollection(features)
            polygon_json = dumps(feature_collection)
            draw = folium.GeoJson(
                polygon_json,
                style_function=lambda feature: {
                    'fillColor': color_dict[key],
                    'color': color,
                    'weight': weight,
                    'dashArray': dash_array,
                    'fillOpacity': fill_opacity,
                }, tooltip=folium.features.GeoJsonTooltip(fields=['id'],
                                                          labels=labels,
                                                          sticky=sticky,
                                                          ))
            feature_group.add_child(draw)
            self.map.add_child(feature_group)
        return self.map

