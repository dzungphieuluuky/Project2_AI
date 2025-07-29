from cell import Cell

class KnowledgeBase:
    def __init__(self) -> None:
        self.clauses = [
            {"~P00"},
            {"~W00"}
        ]

    def add_clause(self, clause : str) -> None:
        clause_set = set(clause)
        if clause_set not in self.clauses:
            self.clauses.append(clause_set)

    # def get_clauses(self):
    #     return self.clauses

    def negate(self, literal: str) -> str:
        return literal[1:] if literal.startswith("~") else "~" + literal

    def resolve_pair(self, ci: set[str], cj: set[str]) -> list[set[str]]:
        resolvents = []
        for li in ci:
            for lj in cj:
                if li == self.negate(lj):
                    new_clause = (ci - {li}) | (cj - {lj})
                    if not self._is_tautology(new_clause):
                        resolvents.append(new_clause)
        return resolvents

    def _is_tautology(self, clause: str) -> bool:
        # Một mệnh đề là tautology nếu chứa literal và phủ định của nó
        return any(self.negate(lit) in clause for lit in clause)

    def full_resolution_closure(self) -> None:
        from itertools import combinations
        added_new = True
        while added_new:
            added_new = False
            new_clauses = []

            for (ci, cj) in combinations(self.clauses, 2):
                resolvents = self.resolve_pair(ci, cj)
                for res in resolvents:
                    if res not in self.clauses and res not in new_clauses:
                        new_clauses.append(res)
                        added_new = True

            self.clauses.extend(new_clauses)

    def get_Adjacents(self, i: int, j: int) -> list[tuple[int, int]]:
        adj = []
        if i - 1 >= 0:
            adj.append((i - 1, j))
        if i + 1 < self.size:
            adj.append((i + 1, j))
        if j - 1 >= 0:
            adj.append((i, j - 1))
        if j + 1 < self.size:
            adj.append((i, j + 1))
        return adj
    
    def tell(self, percepts: dict, location: tuple[int, int]) -> None:
        x, y = location
        adjacents = self.get_Adjacents(x, y)

        # Breeze
        if percepts.get("breeze", default=False) == True:
            clause = {f"P{nx}{ny}" for (nx, ny) in adjacents}
            self.add_clause(clause)
        else:
            for (nx, ny) in adjacents:
                self.add_clause({f"~P{nx}{ny}"})

        # Stench
        if percepts.get("stench", default=False) == True:
            clause = {f"W{nx}{ny}" for (nx, ny) in adjacents}
            self.add_clause(clause)
        else:
            for (nx, ny) in adjacents:
                self.add_clause({f"~W{nx}{ny}"})
    
    def infer_safe_and_dangerous_tiles(self, listTiles: list[list[Cell]]):
        for x in range(self.size):
            for y in range(self.size):
                pid = f"P{x}{y}"
                wid = f"W{x}{y}"

                # Kiểm tra nếu tồn tại mệnh đề đơn khẳng định chắc chắn
                definitely_p = {pid} in self.clauses
                definitely_w = {wid} in self.clauses

                # Kiểm tra nếu tồn tại mệnh đề đơn phủ định cả pit và wumpus
                definitely_not_p = {f"~{pid}"} in self.clauses
                definitely_not_w = {f"~{wid}"} in self.clauses

                cell = listTiles[x][y]
                if definitely_p or definitely_w:
                    cell.markDangerous()
                elif definitely_not_p and definitely_not_w:
                    cell.markSafe()

