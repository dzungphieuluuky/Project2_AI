from agent import Agent
import json
from world import WumpusWorld

def main():
    world_size = input("World Size? (a number/enter to use default): ").lower()
    if len(world_size) == 0:
        world_size = 8
    else: 
        world_size = int(world_size)

    num_wumpus = input("Number of Wumpus (a number/enter to use default): ").lower()
    if len(num_wumpus) == 0:
        num_wumpus = 2
    else:
        num_wumpus = int(num_wumpus)
    
    pit_prob = input("Pit probability (a number/enter to use default): ")
    if len(pit_prob) == 0:
        pit_prob = 0.2
    else:
        pit_prob = float(pit_prob)

    random_agent_input = input("Random Agent (y/n)? ").lower()
    if (random_agent_input == "y"):
        random_agent_input = True
        agent = Agent(random=True)
    else:
        random_agent_input = False
        agent = Agent(random=False)

    wumpus_moving_input = input("Moving Wumpus (y/n)? ").lower()
    if (wumpus_moving_input == "y"):
        wumpus_moving_input = True
        world = WumpusWorld(size=world_size, num_wumpus=num_wumpus, pit_prob=pit_prob, agent=agent, moving_wumpus=True)
    else:
        wumpus_moving_input = False
        world = WumpusWorld(size=world_size, num_wumpus=num_wumpus, pit_prob=pit_prob, agent=agent, moving_wumpus=False)
    
    # get initial state
    initial_state = {}
    for cell_row in world.listCells:
        for cell in cell_row:
            list_state = [cell.name_state[i] for i, state in enumerate(cell.states()) if state]
            initial_state[str(cell.location)] = list_state

    agent_actions = []

    print("GAME STARTED")
    print("Game Symbol Definition:")
    print("Pit: 🫓")
    print("Breeze: 💨")
    print("Wumpus: 👻")
    print("Stench: 💩")
    print("Gold: 🥇")
    print("Agent: 🤖")
    print("Safe: ✅")
    print("Dangerous: ❌")
    print("Visited: 👁️")

    while agent.alive and not agent.out:
        print(f"🏚️ Agent's current location: {agent.location}")
        print(f"↗️ Agent's current direction: {agent.direction}")
        print(f"🦾 Action selected: {agent.selected_action}")
        print(f"💯 Score: {agent.score}")
        print(f"🪙 Gold: {agent.has_gold}")
        print(f"🏹 Arrow: {agent.has_arrow}")

        'B1: lấy percept và cập nhật KB'
        agent.percepts = world.tell_agent_percept()
        print(f"🧠 Percepts: {agent.percepts}")
        world.reset_scream_bump()

        world.tell_agent_adjacent_cells()
        agent.tell()
        world.update_agent_known_cells()
        agent.infer_surrounding_cells()


        'B2: agent chọn hành động'
        action = agent.select_action()
        agent_actions.append(agent.actions[action])

        'B3: Cập nhật trạng thái'
        world.update_world(action=action)
        agent.visited_locations.add(agent.location)

        'B4: show world and knowledge'
        world.printWorld()
        agent.show_knowledge()

    print("🎯 Game Over!")
    print(f"💯 Final Score: {agent.score}")
    print(f"Number of actions: {len(agent_actions)}")

    # get final state
    final_state = {}
    for cell_row in world.listCells:
        for cell in cell_row:
            list_state = [cell.name_state[i] for i, state in enumerate(cell.states()) if state]
            final_state[str(cell.location)] = list_state

    return {
        "world_size": world.size,
        "num_wumpus": world.numWumpus,
        "moving_wumpus": world.moving_wumpus,
        "pit_prob": world.p,
        "random_agent": random_agent_input,
        "agent_action_log": agent_actions,
        "initial_state": initial_state,
        "final_state": final_state
    }

if __name__ == "__main__":
    main()
