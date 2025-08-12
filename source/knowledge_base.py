from cell import Cell

class KnowledgeBase:
    def __init__(self) -> None:
        self.clauses = [
            {"~P0-0"},
            {"~W0-0"}
        ]

    def add_clause(self, clause) -> None:
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
        
        # Xóa các clause chứa unit clause
        unit_clauses = [c for c in self.clauses if len(c) == 1]
        to_remove = []
        for unit in unit_clauses:
            for clause in self.clauses:
                if clause != unit and unit <= clause:
                    to_remove.append(clause)
        # Loại bỏ trùng và xóa khỏi KB
        for clause in set(map(tuple, to_remove)):
            clause_set = set(clause)
            if clause_set in self.clauses:
                self.clauses.remove(clause_set)
    
    def tell(self, percepts, location: tuple[int, int], adjacents: list[tuple[int, int]]):
        x, y = location
        # Breeze xử lý giống tell cũ
        if percepts.get("breeze", False):
            clause = {f"P{nx}-{ny}" for (nx, ny) in adjacents}
            self.add_clause(clause)
        else:
            for (nx, ny) in adjacents:
                self.add_clause({f"~P{nx}-{ny}"})

        # Stench xử lý đặc biệt cho Wumpus di chuyển
        if percepts.get("stench", False):
            # Xóa tất cả các clause đơn ~W ở ô bên cạnh
            for (nx, ny) in adjacents:
                neg_w = {f"~W{nx}-{ny}"}
                if neg_w in self.clauses:
                    self.clauses.remove(neg_w)
            # Thêm clause như bình thường
            clause = {f"W{nx}-{ny}" for (nx, ny) in adjacents}
            self.add_clause(clause)
        else:
            # Xóa tất cả các clause đơn W ở ô bên cạnh
            for (nx, ny) in adjacents:
                w = {f"W{nx}-{ny}"}
                if w in self.clauses:
                    self.clauses.remove(w)
            # Thêm clause phủ định như bình thường
            for (nx, ny) in adjacents:
                self.add_clause({f"~W{nx}-{ny}"})
    
    def infer_safe_and_dangerous_cells(self, knownCells: list[Cell]) -> None:
        for cell in knownCells:
            x, y = cell.location
            pid = f"P{x}-{y}"
            wid = f"W{x}-{y}"

            # Kiểm tra nếu tồn tại mệnh đề đơn khẳng định chắc chắn
            definitely_p = {pid} in self.clauses
            definitely_w = {wid} in self.clauses

            # Kiểm tra nếu tồn tại mệnh đề đơn phủ định cả pit và wumpus
            definitely_not_p = {f"~{pid}"} in self.clauses
            definitely_not_w = {f"~{wid}"} in self.clauses

            if definitely_p or definitely_w:
                cell.markDangerous()
            elif definitely_not_p and definitely_not_w:
                cell.markSafe()

    def percepts_after_shoot(self, start_location: tuple[int, int], direction: str, percepts: dict, 
                             knownCells: list[Cell], size: int) -> bool:
        x, y = start_location
        dx, dy = 0, 0
        if direction == "UP":
            dx, dy = 0, 1
        elif direction == "DOWN":
            dx, dy = 0, -1
        elif direction == "LEFT":
            dx, dy = -1, 0
        elif direction == "RIGHT":
            dx, dy = 1, 0

        # Nếu nghe tiếng hét
        if percepts.get("scream", False):
            first_wumpus_pos = None
            while 0 <= x + dx < size and 0 <= y + dy < size:
                x += dx
                y += dy
                wid = f"W{x}-{y}"
                if {wid} in self.clauses:
                    first_wumpus_pos = (x, y)
                    break
                elif {f"~{wid}"} not in self.clauses:
                    return False
            if first_wumpus_pos:
                self.remove_wumpus(first_wumpus_pos, knownCells)
                return True
            return False
        else:
            # Không nghe tiếng hét → tất cả các ô theo hướng này chắc chắn không có Wumpus
            while 0 <= x + dx < size and 0 <= y + dy < size:
                x += dx
                y += dy
                self.add_clause({f"~W{x}-{y}"})
            return False
        
    def remove_wumpus(self, location: tuple[int, int], knownCells: list[Cell]) -> None:
        x, y = location
        target_literals = {f"W{x}-{y}", f"~W{x}-{y}"}

        self.clauses = [
            clause for clause in self.clauses
            if not any(lit in target_literals for lit in clause)
        ]

        self.add_clause({f"~W{x}-{y}"})
        for cell in knownCells:
            if cell.location == (x, y):
                cell.markSafe()
                break
        print("Notice that Wumpus is no longer around here")