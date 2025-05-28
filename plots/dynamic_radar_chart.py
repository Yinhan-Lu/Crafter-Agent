import matplotlib.pyplot as plt
import numpy as np

np.random.seed(0)

# 设置新的数据点和时间步
dynamics = np.array(['CollectTree', 'CraftWoodPickAxe', 'CraftStoneSword', 'CraftIronPickaxe', 'PlaceRock'])
stats_1 = np.array([0.5, 0.55, 0.45, 0.5, 0.55])  # 第一组数据
space_improvement_2 = 1 - stats_1
# generate the second set of data by adding random improvements not exceeding the space_improvement_2
stats_2 = np.clip(stats_1 + np.random.uniform(0, space_improvement_2, len(stats_1)), 0, 1)  # 第二组数据
space_improvement_3 = 1 - stats_2
stats_3 = np.clip(stats_2 + np.random.uniform(0, space_improvement_3, len(stats_2)), 0, 1)  # 第三组数据


# 创建雷达图
angles = np.linspace(0, 2*np.pi, len(dynamics), endpoint=False).tolist()

stats_1 = np.concatenate((stats_1,[stats_1[0]]))
stats_2 = np.concatenate((stats_2,[stats_2[0]]))
stats_3 = np.concatenate((stats_3,[stats_3[0]]))
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.fill(angles, stats_1, color='red', alpha=0.25)
ax.plot(angles, stats_1, color='red', linewidth=2, label='# steps: 1')  # 线条的样式
ax.fill(angles, stats_2, color='blue', alpha=0.25)
ax.plot(angles, stats_2, color='blue', linewidth=2, label='# steps: 2')  # 线条的样式
ax.fill(angles, stats_3, color='green', alpha=0.25)
ax.plot(angles, stats_3, color='green', linewidth=2, label='# steps: 3')  # 线条的样式

# 设置雷达图的标签
ax.set_yticks([0.25, 0.5, 0.75, 1])
ax.set_yticklabels(["0.25", "0.5", "0.75", "1"], color="grey", size=12)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(dynamics)

# 添加图例和显示图形
# ax.legend(loc='upper right')
ax.legend(bbox_to_anchor=(0.85, 1.0), borderaxespad=0.)
ax.set_title('Quality per Dynamic Instance')
plt.show()

# 保存图片
fig.savefig('quality_per_dynamic_instance.png')