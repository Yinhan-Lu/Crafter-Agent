import pygame
from PIL import Image
import base64
import io
import crafter
from utils.config import API_KEY
import openai
import numpy as np
import matplotlib.pyplot as plt
import random
import json
import time
import agents.agents as agents
from game.game_state import *
from game.action_space import *
import cv2
import os
import utils.helper_functions as helper_functions
from datetime import datetime

def run_single_trajectory(env, agent, current_state, current_updater, action_space, num_steps, record_video=False):
    """
    Run a single trajectory of the game for a specified number of steps.
    
    Args:
        env: The game environment
        agent: The agent to control the game
        current_state: The current game state
        current_updater: The game state updater
        action_space: The action space
        num_steps: Number of steps to run
        record_video: Whether to record the gameplay video
        
    Returns:
        tuple: (total_reward, average_response_time, average_token_count)
    """
    # Pygame setup
    pygame.init()
    window_size = (1800, 3000)
    screen = pygame.display.set_mode(window_size)
    clock = pygame.time.Clock()
    running = True

    # Font setup
    font = pygame.font.Font(None, 30)

    # Video recording setup if needed
    out = None
    if record_video:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f'gameplay_{current_time}.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_filename, fourcc, 5.0, window_size)

    frame_count = 0
    done = False
    total_reward = 0
    i = 0

    while i < num_steps and running:
        # Handle quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Render the environment
        game_image = env.render((600, 600))
        full_surface = pygame.Surface(window_size)
        game_surface = pygame.surfarray.make_surface(game_image.transpose((1, 0, 2)))
        full_surface.blit(game_surface, (0, 0))

        # Get the action from the agent
        action = agent.act()
        
        # Map the action to the corresponding number
        move_mapping = {
            'noop':0,
            'move_west': 1,
            'move_east': 2,
            'move_north': 3,
            'move_south': 4,
            'turn_west': 1,
            'turn_east': 2,
            'turn_north': 3,
            'turn_south': 4,
            'collect_wood': 5,
            'collect_grass': 5,
            'collect_iron': 5,
            'collect_stone': 5,
            'collect_diamond': 5,
            'collect_water': 5,
            'collect_coal': 5,
            'attach_cow': 5,
            'sleep':6,
            'place_stone':7,
            'place_table': 8,
            'place_furnace': 9,
            'place_plant':  10,
            'make_wood_pickaxe': 11,
            'make_stone_pickaxe': 12,
            'make_iron_pickaxe': 13,
            'make_wood_sword': 14,
            'make_stone_sword': 15,
            'make_iron_sword': 16,
        }
        action_num = move_mapping.get(action)

        # Display game information
        words = f"""
        closest wood: {current_state.closest_wood}
        current iteration: {i+1}
        language description of the local view: {current_state.lan_wrapper}
        current local view of materials:\n{helper_functions.matrix_to_string(current_state.text_local_view_mat)}
        current local view of objects:\n{helper_functions.matrix_to_string(current_state.text_local_view_obj)}
        walkable areas: {current_state.walkable_description}
        facing direction: {current_state.get_facing_direction()}
        current reasoning: {agent.get_current_reasoning()}
        current observation:{agent.get_current_observation()}
        current action: {agent.get_current_action()}
        target_material: {current_state.target_material}
        target_object: {current_state.target_obj}
        local view of objects: {current_state.text_local_view_obj}
        valid actions: {action_space.get_valid_action_prompt(current_state)}
        invalid actions: {action_space.get_invalid_action_prompt(current_state)}
        """
        inventory_words = f"current inventory: {current_state.get_inventory_string()}"
        
        # Render text
        y_offset = 800
        for line in words.split('\n'):
            text_surface = font.render(line, True, (255, 255, 255))
            full_surface.blit(text_surface, (100, y_offset))
            y_offset += 40

        y_offset = 40
        for line in inventory_words.split('\n'):
            text_surface = font.render(line, True, (255, 255, 255))
            full_surface.blit(text_surface, (620, y_offset))
            y_offset += 40

        # Update display
        screen.blit(full_surface, (0, 0))
        pygame.display.flip()

        # Record video if enabled
        if record_video:
            frame = pygame.surfarray.array3d(full_surface)
            frame = frame.swapaxes(0, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame)
            frame_count += 1

        # Cap the framerate
        clock.tick(5)

        # Perform the action
        obs, reward, done, info = env.step(action_num)
        current_updater.update()
        total_reward += reward
        i += 1

    # Cleanup
    pygame.quit()
    if record_video and out is not None:
        out.release()

    return total_reward, agent.time/i if i > 0 else 0, agent.token_count/i if i > 0 else 0

def run_multiple_trajectories(num_trajectories, steps_per_trajectory, record_video=False):
    """
    Run multiple trajectories of the game.
    
    Args:
        num_trajectories: Number of trajectories to run
        steps_per_trajectory: Number of steps per trajectory
        record_video: Whether to record videos for each trajectory
    """
    results = []
    
    for traj in range(num_trajectories):
        print(f"\nStarting trajectory {traj + 1}/{num_trajectories}")
        
        # Initialize environment and agent
        env = crafter.Env(reward=True)
        env = crafter.Recorder(
            env, './path/to/logdir',
            save_stats=True,
            save_video=False,
            save_episode=False,
        )
        
        api_key = API_KEY

        obs = env.reset()
        world = env._sem_view
        player = env._player
        current_state = GameState()
        current_updater = GameStateUpdater(game_state=current_state, player=player, world=world, env=env)
        current_updater.update()
        action_space = initialize_action_space()
        agent = agents.lan_agent_react_v2(game_state=current_state, action_space=action_space, api_key=api_key)

        # Run the trajectory
        total_reward, avg_response_time, avg_token_count = run_single_trajectory(
            env, agent, current_state, current_updater, action_space, 
            steps_per_trajectory, record_video
        )

        results.append({
            'trajectory': traj + 1,
            'total_reward': total_reward,
            'average_response_time': avg_response_time,
            'average_token_count': avg_token_count
        })

        print(f"\nTrajectory {traj + 1} Results:")
        print(f"Total reward: {total_reward}")
        print(f"Average response time: {avg_response_time:.2f}")
        print(f"Average token count: {avg_token_count:.2f}")

    # Print summary of all trajectories
    print("\nSummary of all trajectories:")
    print("=" * 50)
    for result in results:
        print(f"\nTrajectory {result['trajectory']}:")
        print(f"Total reward: {result['total_reward']}")
        print(f"Average response time: {result['average_response_time']:.2f}")
        print(f"Average token count: {result['average_token_count']:.2f}")

    # Calculate and print averages
    avg_reward = sum(r['total_reward'] for r in results) / len(results)
    avg_response = sum(r['average_response_time'] for r in results) / len(results)
    avg_tokens = sum(r['average_token_count'] for r in results) / len(results)

    print("\nOverall Averages:")
    print(f"Average reward across all trajectories: {avg_reward:.2f}")
    print(f"Average response time across all trajectories: {avg_response:.2f}")
    print(f"Average token count across all trajectories: {avg_tokens:.2f}")

def main():
    # Example usage: Run 3 trajectories with 50 steps each
    run_multiple_trajectories(num_trajectories=1, steps_per_trajectory=2, record_video=True)

if __name__ == "__main__":
    main()