from __init__ import *

trajectory = np.load('./20240607T153854-ach9-len239.npz')
description = trajectory['description']
action = trajectory['action']
# print(action.where(6))
itemindex = np.where(action == 6)
description_1 = description[194: 198]

print(description_1)
print(itemindex)