import yaml
from addict import Dict
from pathlib import Path

def param_config():
    CONFIG_PATH = Path(__file__).parent / 'configs.yaml'

    with open(CONFIG_PATH, 'r') as file:
        data = Dict(yaml.safe_load(file))
        
    return data
    
    
if __name__ == '__main__':
    params = param_config()
    # print(params.llama.parameters)
    print(params.chatgpt.parameters)
    