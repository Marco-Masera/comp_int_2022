import json
import random
from state_reward import StateReward
from quarto_utils import checkState

#This class handles the pre-processing of the datasets stored in dataset/raw

class PreProcessDataset:
    PROCESSED_TARGET = "dataset/pre_processed/output.json"
    def count_state_size(state):
        c = 0
        for i in state: 
            if i>-1: c+=1;
        return c
    def pre_process(paths):
        dataset = None
        processed = dict()
        n = 0
        for path in paths:
            with open(path, 'r') as source:
                dataset = json.load(source)
            for record in dataset['exp']:
                full, winning = checkState(record[0][0])
                if (full or winning):
                    continue 
                n += 1
                count = PreProcessDataset.count_state_size(record[0][0])
                if count in processed:
                    processed[count].append(record)
                else:
                    processed[count] = [record]
        target = int((len(processed[10]) + len(processed[11]) + 8000) / 2)
        to_exp = []
        print(n)
        for key in processed:
            print(f"Key: {key}: {len(processed[key])}:")
        #Debug
        reward = dict()

        for key in processed.keys():
            if (len(processed[key]) > target):
                processed[key] = random.sample(processed[key], target)

            #Debug 
            if not key in reward: reward[key] = {'pos': [], 'neg': [], 'neut':[]}
            for state in processed[key]:
                if state[1] > 0:
                    reward[key]['pos'].append(StateReward.process_state(state[0]) + [state[1]])
                elif state[1] < 0:
                    reward[key]['neg'].append(StateReward.process_state(state[0]) + [state[1]])
                else:
                    reward[key]['neut'].append(StateReward.process_state(state[0]) + [state[1]])
            continue

            #Pre process
            to_exp.extend([StateReward.process_state(s) for s in processed[key]])
            print(f" {min(processed[key], target)} states of size {key}")
        #print(reward)
        
        for key in reward:
            print(f"{key}: {len(reward[key]['pos'])} pos, {len(reward[key]['neut'])} neut, {len(reward[key]['neg'])} neg")

        #Save dataset
        random.shuffle(to_exp)
        with open(PreProcessDataset.PROCESSED_TARGET, 'w') as dataset:
            dataset.write(json.dumps(reward))

    
    def balance(path):
        dataset = None
        processed = dict()
        with open(path, 'r') as source:
            dataset = json.load(source)
        for record in dataset['exp']:
            full, winning = checkState(record[0][0])
            if (full or winning):
                continue 
            count = PreProcessDataset.count_state_size(record[0][0])
            if count in processed:
                processed[count].append(record)
            else:
                processed[count] = [record]
        #Debug
        reward = dict()

        for key in processed.keys():
            #Debug 
            if not key in reward: reward[key] = {'pos': [], 'neg': [], 'neut':[]}
            for state in processed[key]:
                if state[1] > 0:
                    reward[key]['pos'].append(state)
                elif state[1] < 0:
                    reward[key]['neg'].append(state)
                else:
                    reward[key]['neut'].append(state)
        #Save dataset
        to_r = []
        for key in reward.keys():
            target = int((len(reward[key]['neg']) +  len(reward[key]['neut'])) / 2)
            if (len(reward[key]['pos']) > target):
                to_r.extend(random.sample(reward[key]['pos'], target))
            else:
                to_r.extend(reward[key]['pos'])

            if (len(reward[key]['neg']) > target):
                to_r.extend(random.sample(reward[key]['neg'], target))
            else:
                to_r.extend(reward[key]['neg'])

            if (len(reward[key]['neut']) > target):
                to_r.extend(random.sample(reward[key]['neut'], target))
            else:
                to_r.extend(reward[key]['neut'])

        with open(path, 'w') as dataset:
            dataset.write(json.dumps({'exp': to_r}))
    

    def sample_dataset(source, target_1, target_2):
        with open(source, 'r') as source:
            dataset = json.load(source) 
        target = int(len(dataset)/2)
        random.shuffle(dataset)
        with open(target_1, 'w') as dataset:
            dataset[:target].write(json.dumps())
        with open(target_1, 'w') as dataset:
            dataset[target:].write(json.dumps())


#PreProcessDataset.balance("dataset/raw/dataset_length_8_8.json")
PreProcessDataset.pre_process([
    "dataset/raw/dataset_length_8_2.json",
    "dataset/raw/dataset_length_8_3.json",
    "dataset/raw/dataset_length_8_4.json",
    "dataset/raw/dataset_length_8_5.json",
    "dataset/raw/dataset_length_8_6.json",
    "dataset/raw/dataset_length_8_7.json",
    "dataset/raw/dataset_length_8.json",
])