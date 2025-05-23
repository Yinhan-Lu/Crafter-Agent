import sys
sys.path.append('./')
from __init__ import *

env = crafter.Env(seed=1)
env = crafter.Recorder(env, './', save_stats=False, save_video=False, save_episode=False)
env.reset()

env.step(1)
env.get_player_nearby()

reverse_ids = {
  "None": 0,
  "water": 1,
  "grass": 2,
  "stone": 3,
  "path": 4,
  "sand": 5,
  "tree": 6,
  "lava": 7,
  "coal": 8,
  "iron": 9,
  "diamond": 10,
  "table": 11,
  "furnace": 12
}
env.set_up_player_nearby(['zombie', 'zombie', 'zombie', 'zombie', 'zombie', 'zombie', 'zombie', 'zombie', 'zombie', 'zombie', 'zombie'])
env.set_up_player_facing('zombie')
env.set_up_player_facing('zombie')
env.set_up_player_facing('zombie')
env.set_up_player_facing('zombie')
env.set_up_player_facing('zombie')

# env.render()
# print(env.text_description())
# print(type(1) == int)