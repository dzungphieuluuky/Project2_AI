from agent import Agent
from world import WumpusWorld
from knowledge_base import KnowledgeBase
import random

def get_percepts(world: WumpusWorld, x: int, y: int) -> dict:
    """Lấy percept tại vị trí agent hiện tại"""
    tile = world.listCells[x][y]
    return {
        "breeze": tile.getBreeze(),
        "stench": tile.getStench(),
        "glitter": tile.getGold(),
        "bump": False,  # chưa xử lý tường
        "scream": False  # được xử lý khi bắn trúng Wumpus
    }


def main():
    agent = Agent()
    world = WumpusWorld(agent=agent)

    world.listCells[0][0].setPlayer()
    print("Bắt đầu game")

    scream_flag = False
    bump_flag = False

    while agent.alive and not agent.out:
        print(f"Agent đang ở vị trí: {agent.location}, hướng: {agent.direction}")
        print(f"Score: {agent.score}, Gold: {agent.has_gold}, Arrow: {agent.has_arrow}")

        # B1: lấy percept và cập nhật KB
        x, y = agent.location
        percept = get_percepts(world, x, y)
        percept["scream"] = scream_flag
        percept["bump"] = bump_flag
        print(f"Percept: {percept}")
        scream_flag = False
        bump_flag = False

        world.tell_agent_adjacent_cells()
        agent.tell(percept)
        world.update_agent_known_cells()
        agent.infer_surrounding_cells()

        world.printWorld()
        print(agent.kb.clauses)

        # B2: nhập hành động
        if agent.is_random == False:
            action = input("Hành động (forward / left / right / grab / shoot / climb / exit): ").strip().lower()
        else:
            action = random.sample(['f', 'l', 'r', 'g', 's', 'c', 'e'], k=1)[0]

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
                agent.alive = False
                agent.score -= 1000
                

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

        else:
            print("Hành động không hợp lệ.")
            continue

    print("🎯 Trò chơi kết thúc.")
    print(f"Điểm cuối cùng: {agent.score}")

if __name__ == "__main__":
    main()
