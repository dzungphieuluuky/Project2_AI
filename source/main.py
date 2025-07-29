from agent import Agent
from world import WumpusWorld
from knowledge_base import KnowledgeBase
import random

def main():
    random_agent_input = input("Random Agent? (y/n)").lower()
    if (random_agent_input == "y"):
        agent = Agent(random=True)
    else:
        agent = Agent()
    wumpus_moving_input = input("Moving Wumpus? (y/n)").lower()
    if (wumpus_moving_input == "y"):
        world = WumpusWorld(agent=agent, moving_wumpus=True)
    else:
        world = WumpusWorld(agent=agent, moving_wumpus=False)

    world.listCells[0][0].setPlayer()
    print("Bắt đầu game")

    scream_flag = False
    bump_flag = False

    while agent.alive and not agent.out:
        print(f"Agent đang ở vị trí: {agent.location}, hướng: {agent.direction}")
        print(f"Score: {agent.score}, Gold: {agent.has_gold}, Arrow: {agent.has_arrow}")

        # B1: lấy percept và cập nhật KB
        agent.percepts = world.tell_agent_percept()
        agent.percepts["scream"] = scream_flag
        agent.percepts["bump"] = bump_flag
        print(f"Percept: {agent.percepts}")
        scream_flag = False
        bump_flag = False

        world.tell_agent_adjacent_cells()
        agent.tell()
        world.update_agent_known_cells()
        agent.infer_surrounding_cells()

        world.printWorld()
        print(agent.kb.clauses)

        # B2: nhập hành động
        if agent.is_random == False:
            action = input("Hành động (forward / left / right / grab / shoot / climb / exit): ").strip().lower()
        else:
            action = random.sample(['f', 'l', 'r', 'g', 's', 'c', 'e'], k=1)[0]

        if action not in ['f', 'l', 'r', 'g', 's', 'c', 'e']:
            print("Hành động không hợp lệ")
            continue

        if action == "f":
            old_pos = agent.location
            agent.move_forward()
            x, y = agent.location

            # bump nếu ra ngoài
            if not (0 <= x < world.size and 0 <= y < world.size):
                agent.location = old_pos
                bump_flag = True
                continue

            # nếu rơi vào hố hoặc gặp wumpus thì chết
            tile = world.listCells[x][y]
            if tile.getPit() or tile.getWumpus():
                print(" Agent đã chết!")
                agent.die()
                

            # an toàn → cập nhật ~Wxy và ~Pxy vào KB
            agent.update_kb()

            world.movePlayer(old_pos, agent.location)

        elif action == "l":
            agent.turn_left()

        elif action == "r":
            agent.turn_right()

        elif action == "g":
            x, y = agent.location
            if world.grabGold(x, y):
                agent.grab()

        elif action == "s":
            if agent.shoot():
                dx, dy = 0, 0
                if agent.direction == "UP":
                    dx, dy = 0, 1
                elif agent.direction == "DOWN":
                    dx, dy = 0, -1
                elif agent.direction == "LEFT":
                    dx, dy = -1, 0
                elif agent.direction == "RIGHT":
                    dx, dy = 1, 0

                x, y = agent.location
                while 0 <= x + dx < world.size and 0 <= y + dy < world.size:
                    x += dx
                    y += dy
                    if world.killWumpus(x, y):
                        scream_flag = True
                        break

        elif action == "c":
            agent.climb_out()

        elif action == "e":
            break

        if world.moving_wumpus:
            world.counter += 1
            if world.counter % 5 == 0:
                world.move_all_wumpuses()

    print("🎯 Trò chơi kết thúc.")
    print(f"Điểm cuối cùng: {agent.score}")

if __name__ == "__main__":
    main()
