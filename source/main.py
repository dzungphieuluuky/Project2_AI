from agent import Agent
from world import WumpusWorld
from knowledge_base import KnowledgeBase
import random

def main():
    random_agent_input = input("Random Agent? (y/n)").lower()
    if (random_agent_input == "y"):
        agent = Agent(random=True)
    else:
        agent = Agent(random=False)
    wumpus_moving_input = input("Moving Wumpus? (y/n)").lower()
    if (wumpus_moving_input == "y"):
        world = WumpusWorld(agent=agent, moving_wumpus=True)
    else:
        world = WumpusWorld(agent=agent, moving_wumpus=False)

    print("Bắt đầu game")

    while agent.alive and not agent.out and not agent.exit:
        print(f"Agent đang ở vị trí: {agent.location}, hướng: {agent.direction}")
        print(f"Score: {agent.score}, Gold: {agent.has_gold}, Arrow: {agent.has_arrow}")

        'B1: lấy percept và cập nhật KB'
        agent.percepts = world.tell_agent_percept()
        print(f"Percept: {agent.percepts}")
        world.reset_scream_bump()

        world.tell_agent_adjacent_cells()
        agent.tell()
        world.update_agent_known_cells()
        agent.infer_surrounding_cells()

        world.printWorld()
        agent.show_knowledge()

        'B2: agent chọn hành động'
        action = agent.select_action()

        'B3: Cập nhật trạng thái'
        world.update_world(action=action)

    print("🎯 Trò chơi kết thúc.")
    print(f"Điểm cuối cùng: {agent.score}")

if __name__ == "__main__":
    main()
