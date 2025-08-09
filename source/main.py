from agent import Agent
from world import WumpusWorld
from knowledge_base import KnowledgeBase

def main():
    world_size = input("World Size? (a number or None): ").lower()
    if world_size == "none":
        world_size = 8
    else: 
        world_size = int(world_size)

    random_agent_input = input("Random Agent (y/n)? ").lower()
    if (random_agent_input == "y"):
        agent = Agent(random=True)
    else:
        agent = Agent(random=False)

    wumpus_moving_input = input("Moving Wumpus (y/n)? ").lower()
    if (wumpus_moving_input == "y"):
        world = WumpusWorld(size=world_size, agent=agent, moving_wumpus=True)
    else:
        world = WumpusWorld(size=world_size, agent=agent, moving_wumpus=False)
    
    number_of_actions = 0

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

    while agent.alive and not agent.out and not agent.is_exit:
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
        number_of_actions += 1

        'B3: Cập nhật trạng thái'
        world.update_world(action=action)
        agent.visited_locations.add(agent.location)

        'B4: show world and knowledge'
        world.printWorld()
        agent.show_knowledge()

    print("🎯 Game Over!")
    print(f"💯 Final Score: {agent.score}")
    print(f"Number of actions: {number_of_actions}")

if __name__ == "__main__":
    main()
