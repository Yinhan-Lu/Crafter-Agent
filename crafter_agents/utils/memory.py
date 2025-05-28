from collections import deque
from dataclasses import dataclass

@dataclass
class StepMemory:
    reasoning:str
    observation:str
    current_step:int
    action:str

class Recent_Results:
    def __init__(self,num_of_results):
        self.num_of_results = num_of_results
        self.result_buffer:deque[StepMemory] = deque(maxlen = self.num_of_results)

    def add_result(self, reasoning, observation, current_step, action):
        self.result_buffer.append(StepMemory(reasoning, current_step, action))

    
    def get_recent_results_as_string(self):
        return "\n".join([f"In Step {result.current_step},Observation: {result.observation}, Reasoning: {result.reasoning}\nAction after reasoning of the observation in step {result.current_step}: {result.action}" for result in self.result_buffer])





        

    