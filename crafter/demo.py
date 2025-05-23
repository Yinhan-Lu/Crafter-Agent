import numpy as np

loaded_file = np.load('./new_trajectory/seed_6/20240608T122439-ach20-len478.npz')
action = loaded_file['action']
index = np.where(action == 9)[0][0]
description = loaded_file['description']
print(description[index-1])
print('====================')
print(description[index])