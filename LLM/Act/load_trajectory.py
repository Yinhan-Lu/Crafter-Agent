import sys
import cv2
import json
import argparse
sys.path.append('./')
from utils import *
from __init__ import *
import numpy as np

def draw_text_on_image(image, text, position=(50, 50), color=(0, 255, 0), font_scale=0.3, thickness=1):
    """
    Draws specified text on the given image with enhanced visibility.
    """
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)
    if not image.flags['C_CONTIGUOUS']:
        image = np.ascontiguousarray(image)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, position, font, font_scale, color, thickness, cv2.LINE_AA)


def load_trajectory(trajectory_dir, env_seed=1, initial_size=(600, 600), record_path='./trajectory'):
    env = crafter.Env(seed=env_seed)
    env = crafter.Recorder(env, record_path, save_video=False, save_episode=False, save_stats=False)
    env.reset()
    print('Diamonds exist:', env._world.count('diamond'))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Define the codec
    frame_size = initial_size
    video_size = (frame_size[1], frame_size[0])
    save_path = os.path.join(trajectory_dir, 'trajectory.mp4')
    out = cv2.VideoWriter(save_path, fourcc, 5.0, video_size)

    with open(os.path.join(trajectory_dir, 'trajectory.json'), 'r') as f:
        trajectory = json.load(f)

    time_step = 0
    prev_subtask = None
    for transition_step in trajectory:
        transition = trajectory[transition_step]
        subgoal = transition['subgoal']
        subtask = transition['subtask']

        action = transition['action']
        subtask_name = subtask['subtask']
        # if transition['subtask'] != prev_subtask:
        #     print('termination:', transition['termination'], '\n')
        #     print('Subtask:', transition['subtask'])
        #     if 'evolved_dynamics' in transition.keys():
        #         print('Evolved dynamics:', transition['evolved_dynamics'])
        #     print('============================================================')
        #     prev_subtask = transition['subtask']

        if f'{time_step}.png' in os.listdir(os.path.join(trajectory_dir, 'images')):
            rgb_obs = cv2.imread(os.path.join(trajectory_dir, 'images', f'{time_step}.png'))

            draw_text_on_image(rgb_obs, f'Subgoal: {subgoal}', (0, 570))
            draw_text_on_image(rgb_obs, f'Subtask: {subtask_name}', (0, 590))
            
            out.write(rgb_obs)
        time_step += 1

    out.release()


def visualize_map(external_map, image_size=16, map_size=64, assets_dir='./Act/assets'):
    assets = dict()
    for asset in os.listdir(assets_dir):
        asset_name = asset.removesuffix('.png')
        assets[asset_name] = Image.open(os.path.join(assets_dir, asset))

    canvas = Image.new('RGBA', (map_size*image_size, map_size*image_size))
    for y, row in enumerate(external_map):
        for x, element in enumerate(row):
            canvas.paste(assets[element], (x * image_size, y * image_size))

    open_cv_image = np.array(canvas)
    open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    return open_cv_image


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=10)
    parser.add_argument('--trajectory_dir', type=str, default='./Act/trajectory/0/2024-06-12_01-17-47', help="Path to the trajectory file.")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    load_trajectory(trajectory_dir=args.trajectory_dir, env_seed=args.seed)