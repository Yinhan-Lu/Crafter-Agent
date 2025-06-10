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
from agents.structured_prompts import get_recent_results_prompt
from datetime import datetime
import textwrap

def wrap_text(text, font, max_width):
    """
    Wrap text to fit within a given width.
    
    Args:
        text: The text to wrap
        font: The pygame font object
        max_width: Maximum width in pixels
        
    Returns:
        List of wrapped lines
    """
    if not text or text == "None":
        return ["N/A"]
    
    # Clean up the text
    text = str(text).strip()
    if not text:
        return ["N/A"]
    
    # Estimate characters per line based on font size
    char_width = font.size("A")[0]
    chars_per_line = max(10, max_width // char_width - 2)
    
    # Wrap the text
    wrapped_lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            wrapped_lines.append("")
            continue
        lines = textwrap.wrap(paragraph, width=chars_per_line)
        if not lines:
            lines = [""]
        wrapped_lines.extend(lines)
    
    return wrapped_lines

def render_text_block(surface, text, font, x, y, max_width, max_height, color=(255, 255, 255)):
    """
    Render a block of text with proper wrapping and height limits.
    
    Returns:
        int: The Y position after rendering (for stacking text blocks)
    """
    if not text:
        text = "N/A"
        
    wrapped_lines = wrap_text(text, font, max_width)
    line_height = font.get_height() + 2
    max_lines = max_height // line_height
    
    current_y = y
    lines_rendered = 0
    
    for line in wrapped_lines:
        if lines_rendered >= max_lines - 1:  # Save space for "..." if needed
            if lines_rendered < len(wrapped_lines):
                text_surface = font.render("...", True, color)
                surface.blit(text_surface, (x, current_y))
            break
            
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, current_y))
        current_y += line_height
        lines_rendered += 1
    
    return current_y

def render_matrix_visual(surface, matrix, title, x, y, font, cell_size=15):
    """
    Render a 9x9 matrix as a visual grid with a title.
    
    Args:
        surface: Pygame surface to draw on
        matrix: 9x9 matrix to visualize
        title: Title for the matrix
        x, y: Position to draw at
        font: Font for labels
        cell_size: Size of each cell in pixels
        
    Returns:
        int: Y position after the matrix
    """
    # Render title
    title_surface = font.render(title, True, (255, 255, 255))
    surface.blit(title_surface, (x, y))
    y += font.get_height() + 5
    
    if not matrix or len(matrix) == 0:
        error_surface = font.render("No data", True, (255, 100, 100))
        surface.blit(error_surface, (x, y))
        return y + font.get_height()
    
    # Color mapping for different materials/objects
    color_map = {
        'grass': (34, 139, 34),    # Forest green
        'tree': (0, 100, 0),       # Dark green
        'stone': (128, 128, 128),  # Gray
        'water': (0, 191, 255),    # Deep sky blue
        'sand': (238, 203, 173),   # Beige
        'path': (139, 69, 19),     # Saddle brown
        'coal': (36, 36, 36),      # Dark gray
        'iron': (184, 134, 11),    # Dark golden rod
        'diamond': (185, 242, 255), # Light cyan
        'lava': (255, 69, 0),      # Red orange
        'player': (255, 255, 0),   # Yellow
        'Cow': (139, 69, 19),      # Brown
        'Zombie': (255, 0, 0),     # Red
        'Skeleton': (255, 255, 255), # White
        'Nothing': (0, 0, 0),      # Black
        'table': (160, 82, 45),    # Saddle brown
        'furnace': (105, 105, 105) # Dim gray
    }
    
    # Transpose the matrix to match game view orientation
    # The game uses a different coordinate system than our matrix
    transposed_matrix = list(zip(*matrix)) if matrix else []
    
    # Draw the grid
    for row in range(min(9, len(transposed_matrix))):
        for col in range(min(9, len(transposed_matrix[row]) if row < len(transposed_matrix) else 0)):
            cell_x = x + col * cell_size
            cell_y = y + row * cell_size
            
            # Get cell value and color
            cell_value = transposed_matrix[row][col] if row < len(transposed_matrix) and col < len(transposed_matrix[row]) else 'Nothing'
            cell_color = color_map.get(cell_value, (64, 64, 64))  # Default gray
            
            # Draw cell
            pygame.draw.rect(surface, cell_color, (cell_x, cell_y, cell_size-1, cell_size-1))
            
            # Highlight player position (center)
            if row == 4 and col == 4:
                pygame.draw.rect(surface, (255, 255, 0), (cell_x, cell_y, cell_size-1, cell_size-1), 2)
    
    return y + 9 * cell_size + 10

def run_single_trajectory(env, agent, current_state, current_updater, action_space, num_steps, record_video=False, video_output_dir=None):
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
        video_output_dir: Directory to save videos (default: current directory)
        
    Returns:
        tuple: (total_reward, average_response_time, average_token_count)
    """
    # Pygame setup
    pygame.init()
    window_size = (1600, 1200)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Crafter Agent Gameplay")
    clock = pygame.time.Clock()
    running = True

    # Font setup
    title_font = pygame.font.Font(None, 24)
    header_font = pygame.font.Font(None, 20)
    text_font = pygame.font.Font(None, 16)
    small_font = pygame.font.Font(None, 14)  # Smaller font for detailed descriptions

    # Layout dimensions
    game_area_width = 600
    info_area_width = window_size[0] - game_area_width - 20
    info_area_x = game_area_width + 10

    # Video recording setup if needed
    out = None
    if record_video:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if video_output_dir:
            os.makedirs(video_output_dir, exist_ok=True)
            video_filename = os.path.join(video_output_dir, f'gameplay_{current_time}.mp4')
        else:
            video_filename = f'gameplay_{current_time}.mp4'
        
        print(f"Recording video to: {video_filename}")
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

        # Clear screen
        screen.fill((0, 0, 0))

        # Render the game environment
        game_image = env.render((game_area_width, game_area_width))
        game_surface = pygame.surfarray.make_surface(game_image.transpose((1, 0, 2)))
        screen.blit(game_surface, (0, 0))

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

        # Information panel
        y_pos = 10
        
        # Step number (prominent)
        step_title = f"=== STEP {i+1}/{num_steps} ==="
        step_surface = title_font.render(step_title, True, (255, 255, 0))
        screen.blit(step_surface, (info_area_x, y_pos))
        y_pos += 35

        # Current action (highlighted)
        action_text = f"ACTION: {action}"
        action_surface = header_font.render(action_text, True, (0, 255, 0))
        screen.blit(action_surface, (info_area_x, y_pos))
        y_pos += 30

        # Player stats
        stats_text = f"Health: {current_state.health}/9  Food: {current_state.food}/9  Drink: {current_state.drink}/9  Energy: {current_state.energy}/9"
        stats_surface = text_font.render(stats_text, True, (255, 255, 255))
        screen.blit(stats_surface, (info_area_x, y_pos))
        y_pos += 25

        # Target info
        target_text = f"Target: {current_state.target_material} | Facing: {current_state.get_facing_direction()}"
        target_surface = text_font.render(target_text, True, (255, 255, 255))
        screen.blit(target_surface, (info_area_x, y_pos))
        y_pos += 30

        # Goal section - Main objective and current subgoal
        goal_header = header_font.render("🎯 GOALS:", True, (255, 215, 0))  # Gold color
        screen.blit(goal_header, (info_area_x, y_pos))
        y_pos += 25
        
        # Main objective (fixed goal)
        main_goal_text = "Main: Find and collect a diamond"
        main_goal_surface = text_font.render(main_goal_text, True, (255, 255, 255))
        screen.blit(main_goal_surface, (info_area_x, y_pos))
        y_pos += 20
        
        # Current subgoal (dynamic)
        try:
            from planning.sub_goal_manager import SubgoalManager
            subgoal_manager = SubgoalManager()
            subgoal_manager.update_plan(current_state)
            current_subgoal = subgoal_manager.get_current_subgoal()
        except Exception as e:
            current_subgoal = f"Error: {str(e)}"
        
        # Render subgoal with wrapping
        subgoal_text = f"Current: {current_subgoal}"
        y_pos = render_text_block(screen, subgoal_text, text_font, info_area_x, y_pos, 
                                info_area_width, 60, (144, 238, 144))  # Light green color
        y_pos += 15

        # 9x9 Area Visualization
        header_surface = header_font.render("9x9 AREA - MATERIALS:", True, (255, 255, 0))
        screen.blit(header_surface, (info_area_x, y_pos))
        y_pos += 25
        
        if current_state.text_local_view_mat:
            y_pos = render_matrix_visual(screen, current_state.text_local_view_mat, 
                                       "Materials", info_area_x, y_pos, text_font, cell_size=12)
        y_pos += 10

        header_surface = header_font.render("9x9 AREA - OBJECTS:", True, (255, 255, 0))
        screen.blit(header_surface, (info_area_x, y_pos))
        y_pos += 25
        
        if current_state.text_local_view_obj:
            y_pos = render_matrix_visual(screen, current_state.text_local_view_obj, 
                                       "Objects", info_area_x, y_pos, text_font, cell_size=12)
        y_pos += 15

        # Natural language description of 9x9 area
        lang_header = header_font.render("9x9 AREA - DESCRIPTION:", True, (255, 255, 0))
        screen.blit(lang_header, (info_area_x, y_pos))
        y_pos += 25
        
        if current_state.lan_wrapper:
            y_pos = render_text_block(screen, current_state.lan_wrapper, small_font, info_area_x, y_pos, 
                                    info_area_width, 350, (200, 200, 255))  # Increased from 200 to 350 pixels to show full content
        y_pos += 15

        # Precise 3x3 area description
        precise_3x3_header = header_font.render("3x3 PRECISE DIRECTIONS:", True, (255, 255, 0))
        screen.blit(precise_3x3_header, (info_area_x, y_pos))
        y_pos += 25
        
        # Import and use the precise 3x3 description function
        from agents.structured_prompts import get_precise_3x3_area_description
        precise_3x3_description = get_precise_3x3_area_description(current_state)
        y_pos = render_text_block(screen, precise_3x3_description, small_font, info_area_x, y_pos, 
                                info_area_width, 200, (144, 238, 144))  # Light green color
        y_pos += 15

        # Current observation
        obs_header = header_font.render("OBSERVATION:", True, (0, 255, 255))
        screen.blit(obs_header, (info_area_x, y_pos))
        y_pos += 25
        
        observation = agent.get_current_observation()
        y_pos = render_text_block(screen, observation, text_font, info_area_x, y_pos, 
                                info_area_width, 100, (255, 255, 255))
        y_pos += 15

        # Current reasoning
        reasoning_header = header_font.render("REASONING:", True, (255, 165, 0))
        screen.blit(reasoning_header, (info_area_x, y_pos))
        y_pos += 25
        
        reasoning = agent.get_current_reasoning()
        y_pos = render_text_block(screen, reasoning, text_font, info_area_x, y_pos, 
                                info_area_width, 120, (255, 255, 255))
        y_pos += 15

        # Inventory (compact)
        inv_header = header_font.render("INVENTORY:", True, (255, 255, 255))
        screen.blit(inv_header, (info_area_x, y_pos))
        y_pos += 20
        
        # Show only non-zero inventory items
        inv_items = []
        for item, count in current_state.inventory.items():
            if count > 0:
                inv_items.append(f"{item}:{count}")
        
        if inv_items:
            inv_text = " | ".join(inv_items)
            y_pos = render_text_block(screen, inv_text, text_font, info_area_x, y_pos, 
                                    info_area_width, 60, (255, 255, 255))
            
        # Valid actions
        valid_actions = action_space.get_valid_actions(current_state)
        
        
        # Show valid actions
        if valid_actions:
            valid_text = "Valid Actions: " + ", ".join(valid_actions)
            y_pos = render_text_block(screen, valid_text, text_font, info_area_x, y_pos, 
                                    info_area_width, 60, (144, 238, 144))
            y_pos += 15

        # Show the recent results
        recent_results = get_recent_results_prompt(agent.recent_results)
        if recent_results:
            recent_text = "Recent Results: " + recent_results
            y_pos = render_text_block(screen, recent_text, text_font, info_area_x, y_pos, 
                                    info_area_width, 60, (144, 238, 144))
            y_pos += 15
        
        

        # Update display
        pygame.display.flip()

        # Record video if enabled
        if record_video:
            frame = pygame.surfarray.array3d(screen)
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
        print(f"Video saved successfully!")

    return total_reward, agent.time/i if i > 0 else 0, agent.token_count/i if i > 0 else 0

def run_multiple_trajectories(num_trajectories, steps_per_trajectory, record_video=False, video_output_dir=None):
    """
    Run multiple trajectories of the game.
    
    Args:
        num_trajectories: Number of trajectories to run
        steps_per_trajectory: Number of steps per trajectory
        record_video: Whether to record videos for each trajectory
        video_output_dir: Directory to save videos (default: current directory)
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
            steps_per_trajectory, record_video, video_output_dir
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
    # Example usage with custom video location
    
    # Option 1: Save to a specific directory
    # run_multiple_trajectories(num_trajectories=1, steps_per_trajectory=10, 
    #                          record_video=True, video_output_dir="./videos")
    
    # Option 2: Save to absolute path
    # run_multiple_trajectories(num_trajectories=1, steps_per_trajectory=10,
    #                          record_video=True, video_output_dir="/Users/admin/Desktop/gameplay_videos")
    
    # Option 3: Save to current directory (default behavior)
    run_multiple_trajectories(num_trajectories=1, steps_per_trajectory=200, record_video=True, video_output_dir="./videos")

if __name__ == "__main__":
    main()