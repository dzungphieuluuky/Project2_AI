from agent import Agent
from world import WumpusWorld
import json
import random

def get_testcase(world_size, num_wumpus, pit_prob, random_agent_input, wumpus_moving_input):
    agent = Agent(random=random_agent_input)
    world = WumpusWorld(size=world_size, num_wumpus=num_wumpus, pit_prob=pit_prob, agent=agent, moving_wumpus=wumpus_moving_input)
    
    agent_actions = []

    # main loop
    while agent.alive and not agent.out:

        'B1: lấy percept và cập nhật KB'
        agent.get_percepts_from(world)
        world.reset_scream_bump()

        agent.tell()
        world.update_agent_known_cells()
        agent.infer_surrounding_cells()

        'B2: agent chọn hành động'
        action = agent.select_action()
        agent_actions.append(agent.name_actions[action])

        'B3: Cập nhật trạng thái'
        world.update_world(action=action)
        agent.update_visited_location()

    # get final state
    final_state = {}
    for cell_row in world.listCells:
        for cell in cell_row:
            list_state = [cell.name_state[i] for i, state in enumerate(cell.states()) if state]
            final_state[str(cell.location)] = list_state

    return {
        "world_size": world.size,
        "num_wumpus": world.numWumpus,
        "pit_prob": world.p,
        "random_agent": random_agent_input,
        "moving_wumpus": world.moving_wumpus,
        "agent_action_log": agent_actions,
        "final_state": final_state
    }
if __name__ == "__main__":
    for i in range(20):
        file_name = f"Test_case_{i}"
        world_size = random.randint(8, 35)
        num_wumpus = random.randint(2, 5)
        pit_prob = random.randint(1, 4) / 10
    
        random_agent = random.choice([True, False])
        wumpus_moving = random.choice([True, False])

        game_config = get_testcase(world_size, num_wumpus, pit_prob,
                                   random_agent, wumpus_moving)
        with open(f"testcases/{file_name}.json", mode="w") as file:
            json.dump(game_config, file, indent=4)
