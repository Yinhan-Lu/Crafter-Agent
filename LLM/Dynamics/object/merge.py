import sys
sys.path.append('./')
from __init__ import *

import os
import json

def merge(object_dir, save_path):
    merged_relationship = dict()
    for object_name in os.listdir(object_dir):
        relationship = {
            'grass': 0, 'coal': 0, 'cow': 0, 'diamond': 0, 'iron': 0, 'lava': 0, 'skeleton': 0, 'stone': 0, 'tree': 0, 'water': 0, 'zombie': 0, 'path': 0, 'sand': 0,
        }
        if object_name[:-5] in relationship.keys():
            relationship.pop(object_name[:-5])
        with open(os.path.join(object_dir, object_name)) as f:
            dynamics = json.load(f)
        for dynamic_num, dynamic in dynamics.items():
            try:
                valid_relationships = dynamic['valid_relationships']
                for obj, relationship_type in valid_relationships.items():
                    if obj not in relationship.keys():
                        continue    
                    if obj == object_name[:-5]:
                        continue
                    if relationship_type == 'Very related':
                        relationship[obj] += 1
                    elif relationship_type == 'Not related':
                        relationship[obj] -= 1
                    else:
                        print(f'Invalid relationship type: {relationship_type}')
            except:
                continue
        
        top = sorted(relationship.items(), key=lambda x: x[1], reverse=True)[:3]
        bottom = sorted(relationship.items(), key=lambda x: x[1])
        bottom = [item for item in bottom if item[0] != object_name[:-5]][:3]

        # Only store the names, not the values
        merged_relationship[object_name[:-5]] = {
            'top': [item[0] for item in top],
            'bottom': [item[0] for item in bottom]
        }

        print(f'{object_name[:-5]} can be found near {[item[0] for item in top]}, but it is not associated with {[item[0] for item in bottom]}')
    
    with open(save_path, 'w') as f:
        json.dump(merged_relationship, f, indent=4)


if __name__ == '__main__':
    object_dir = 'Dynamics/object/dynamics/verified'
    save_dir = 'Dynamics/object/dynamics/merged'

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = os.path.join(save_dir, 'objects.json')
    merge(object_dir, save_path)