import sys
import copy
import time
from agent import Agent
from world import WumpusWorld
import json

def run_single_headless_game(world, agent):
    """
    Runs a single game instance without any GUI.

    Args:
        world (WumpusWorld): The game world instance.
        agent (Agent): The agent instance to test.

    Returns:
        dict: A dictionary containing the results of the run.
    """
    actions_taken = 0
    max_steps = world.size * world.size * 2 

    while agent.alive and not agent.out:
        if actions_taken > max_steps:
            agent.die()
            break

        agent.get_percepts_from(world)
        world.reset_scream_bump()
        agent.tell()
        world.update_agent_known_cells()
        agent.infer_surrounding_cells()
        
        action_code = agent.select_action()
        world.update_world(action=action_code)
        agent.update_visited_location()
        
        actions_taken += 1

    success = agent.has_gold and agent.out
    return {
        "success": success,
        "score": agent.score,
        "actions": actions_taken
    }

def analyze_and_print_results(logic_stats, random_stats, num_runs, elapsed_time, world_config):
    """Calculates and prints the final statistics"""

    def calculate_metrics(stats):
        if not stats:
            return {
                "success_rate": 0, "avg_score": 0, "avg_actions": 0,
                "avg_actions_on_success": 'ìninity'
            }
        
        success_count = sum(1 for r in stats if r['success'])
        
        successful_runs = [r for r in stats if r['success']]
        total_actions_on_success = sum(r['actions'] for r in successful_runs)
        
        return {
            "success_rate": (success_count / num_runs) * 100,
            "avg_score": sum(r['score'] for r in stats) / num_runs,
            "avg_actions": sum(r['actions'] for r in stats) / num_runs,
            "avg_actions_on_success": total_actions_on_success / success_count if success_count > 0 else 'infinity'
        }

    logic_metrics = calculate_metrics(logic_stats)
    random_metrics = calculate_metrics(random_stats)

    print("\n" + "="*60)
    print("           WUMPUS WORLD AGENT COMPARISON RESULTS")
    print("="*60)
    print(f"Total simulations per agent: {num_runs}")
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")
    print("-"*60)
    
    header = f"{'Metric':<28} | {'Intelligent Agent':^15} | {'Random Agent':^15}"
    print(header)
    print("-"*len(header))

    print(f"{'Success Rate (%)':<28} | {logic_metrics['success_rate']:^15.2f} | {random_metrics['success_rate']:^15.2f}")
    print(f"{'Average Score':<28} | {logic_metrics['avg_score']:^15.2f} | {random_metrics['avg_score']:^15.2f}")
    print(f"{'Avg Actions (All Runs)':<28} | {logic_metrics['avg_actions']:^15.2f} | {random_metrics['avg_actions']:^15.2f}")

    logic_eff = logic_metrics['avg_actions_on_success']
    random_eff = random_metrics['avg_actions_on_success']

    logic_eff_str = f"{logic_eff:.2f}" if isinstance(logic_eff, (int, float)) else logic_eff
    random_eff_str = f"{random_eff:.2f}" if isinstance(random_eff, (int, float)) else random_eff
    print(f"{'Avg Actions (Successful)':<28} | {logic_eff_str:^15} | {random_eff_str:^15}")    
    
    print("="*60)
    print("\n* Avg Actions (Successful) is a measure of decision efficiency.\n")
    results = {
        'num_runs': num_runs,
        'world_configurations': world_config,
        'hybrid_agent_result': logic_metrics,
        'random_agent_result': random_metrics
    }
    with open(f"./experiments/{int(time.time())}.json", mode="w") as file:
            json.dump(results, file, indent=4)

def run_comparison_simulations(num_runs=100, world_size=8, num_wumpus=2, pit_prob=0.2, moving_wumpus=False):
    """
    Runs a series of simulations to compare the intelligent agent
    against the random agent on identical maps.
    """
    logic_agent_stats = []
    random_agent_stats = []
    
    print(f"Starting simulation of {num_runs} runs for each agent...")
    start_time = time.time()

    for i in range(num_runs):
        logic_agent = Agent(random=False)
        master_world = WumpusWorld(
            agent=logic_agent, 
            size=world_size, 
            num_wumpus=num_wumpus, 
            pit_prob=pit_prob,
            moving_wumpus=moving_wumpus
        )
        
        # Test the intelligent agent
        result_logic = run_single_headless_game(master_world, logic_agent)
        logic_agent_stats.append(result_logic)
        
        world_copy = copy.deepcopy(master_world)
        
        random_agent = Agent(random=True)
        world_copy.agent = random_agent
        
        # Test the random agent on the same map
        result_random = run_single_headless_game(world_copy, random_agent)
        random_agent_stats.append(result_random)

        # Print progress
        sys.stdout.write(f"\rProgress: [{('=' * (i + 1)).ljust(num_runs)}] {i + 1}/{num_runs}")
        sys.stdout.flush()

    end_time = time.time()
    world_configurations = {
        'world_size': world_size,
        'number_wumpus': num_wumpus,
        'pit_probability': pit_prob,
        'moving_wumpus': moving_wumpus
    }
    analyze_and_print_results(logic_agent_stats, random_agent_stats, num_runs, end_time - start_time, world_configurations)


if __name__ == "__main__":
    number_of_runs = int(input("Number of runs: "))
    if number_of_runs is None:
        number_of_runs = 100
    world_size = int(input("World Size: "))
    if world_size is None:
        world_size = 8
    num_wumpus = int(input("Number of wumpus: "))
    if num_wumpus is None:
        num_wumpus = 2
    pit_prob = float(input("Pit probability: "))
    if pit_prob is None:
        pit_prob = 0.2
    moving_wumpus = input("Moving wumpus (y/n): ").lower()
    moving_wumpus = True if moving_wumpus == "y" else False
    run_comparison_simulations(
        num_runs=number_of_runs,
        world_size=world_size,
        num_wumpus=num_wumpus,
        pit_prob=pit_prob,
        moving_wumpus=moving_wumpus
    )