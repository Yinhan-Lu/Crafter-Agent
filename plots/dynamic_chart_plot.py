import matplotlib.pyplot as plt
import numpy as np

# 假设数据
timesteps = np.arange(1, 11)  # 10个时间步
# 生成新的数据，确保min, max与mean的差距不超过0.03
adjusted_data = {
    'action_dynamics': {
        'precision': {'mean': np.random.uniform(0.6, 0.9, 10), 'min': lambda x: np.clip(x - 0.03, 0.6, x), 'max': lambda x: np.clip(x + 0.03, x, 1.0)},
        'recall': {'mean': np.random.uniform(0.2, 0.4, 10), 'min': lambda x: np.clip(x - 0.03, 0.2, x), 'max': lambda x: np.clip(x + 0.03, x, 0.5)}
    },
    'object_dynamics': {
        'precision': {'mean': np.random.uniform(0.6, 0.9, 10), 'min': lambda x: np.clip(x - 0.03, 0.6, x), 'max': lambda x: np.clip(x + 0.03, x, 1.0)},
        'recall': {'mean': np.random.uniform(0.2, 0.4, 10), 'min': lambda x: np.clip(x - 0.03, 0.2, x), 'max': lambda x: np.clip(x + 0.03, x, 0.5)}
    }
}

# 配置颜色和标记
colors = {'action_dynamics': 'red', 'object_dynamics': 'green'}
markers = {'action_dynamics': 'o', 'object_dynamics': 's'}
linestyles = {'precision': '-', 'recall': '--'}

# 应用函数生成min和max值
for obj in adjusted_data.values():
    for metric in obj.values():
        mean_values = metric['mean']
        metric['min'] = metric['min'](mean_values)
        metric['max'] = metric['max'](mean_values)

fig, ax = plt.subplots(figsize=(10, 6))



# 重新绘制图形
for obj, metrics in adjusted_data.items():
    for metric, values in metrics.items():
        ax.plot(timesteps, values['mean'], label=f'{obj} {metric} mean', color=colors[obj], linestyle=linestyles[metric], marker=markers[obj])
        ax.fill_between(timesteps, values['min'], values['max'], color=colors[obj], alpha=0.2)

ax.set_xlabel('Evolve Steps')
ax.set_ylabel('Value')
ax.set_title('Quality of Learned Dynamics over Time by Class')
ax.legend(loc='upper right') 
plt.show()

# 保存图片
fig.savefig('quality_per_dynamic_class.png')

