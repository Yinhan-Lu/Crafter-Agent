import argparse
import numpy as np
import sys
sys.path.append('..')
import crafter

def load_trajectory(filepath, env_seed=0, initial_size=(600, 600), record_path='./seed_4_reformat'):
    try:
        trajectory = np.load(filepath)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return

    trajectory_action = trajectory['action'][1:]  # Skip the first action
    trajectory_index = 0

    env = crafter.Env(seed=env_seed)
    env = crafter.Recorder(env, record_path)
    env.reset()

    print('Diamonds exist:', env._world.count('diamond'))

    total_reward = 0.0
    done = False
    while not done:
        env.render(initial_size)
        # env.get_player_standing()

        action = trajectory_action[trajectory_index]
        trajectory_index += 1
        _, reward, done, info = env.step(action)
        total_reward += reward
        if done:
            print('Total reward:', total_reward)
            print('Achievements:', info['achievements'])


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=4)
    parser.add_argument('--filepath', type=str, default='trajectory/seed_4/20240319T220539-ach14-len469.npz', help="Path to the trajectory file.")
    parser.add_argument('--index', type=int, default=-1)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    load_trajectory(filepath=args.filepath, env_seed=args.seed)

