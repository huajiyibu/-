import numpy as np
from collections import Counter
from grid_location import detect_grid


def fill_zero(x, y, grid: np.ndarray) -> np.ndarray:
    '''在位置(x,y)放牛后，将该行、该列、对角线相邻格子标记为-1（不可用）'''
    new_grid = grid.copy()
    rows, cols = grid.shape

    if grid[x, y] == -1:
        return new_grid
    
    for i in range(cols):
        if i != y:
            new_grid[x, i] = -1
    for i in range(rows):
        if i != x:
            new_grid[i, y] = -1
    
    for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols:
            new_grid[nx, ny] = -1
    
    new_grid[x, y] = grid[x, y]
    return new_grid


def row_detection(grid: np.ndarray) -> bool:
    '''检测每行是否至少有一个有效位置'''
    rows, cols = grid.shape
    for i in range(rows):
        if np.all(grid[i, :] == -1):
            return False
    return True


def col_detection(grid: np.ndarray) -> bool:
    '''检测每列是否至少有一个有效位置'''
    rows, cols = grid.shape
    for i in range(cols):
        if np.all(grid[:, i] == -1):
            return False
    return True


def color_detection(grid: np.ndarray, original_grid: np.ndarray) -> bool:
    '''检测每种颜色是否至少有一个有效位置'''
    unique_colors = np.unique(original_grid)
    for color in unique_colors:
        color_mask = (original_grid == color)
        valid_positions = (grid != -1) & color_mask
        if not np.any(valid_positions):
            return False
    return True


def is_valid_choice(grid: np.ndarray, original_grid: np.ndarray, x: int, y: int) -> bool:
    '''检查在位置(x,y)放牛是否是一个有效的选择'''
    if grid[x, y] == -1:
        return False
    
    temp_grid = fill_zero(x, y, grid)
    
    if not row_detection(temp_grid):
        return False
    if not col_detection(temp_grid):
        return False
    if not color_detection(temp_grid, original_grid):
        return False
    
    return True


def color_set_in_range(grid: np.ndarray, original_grid: np.ndarray, start, end, axis=0):
    '''获取指定范围内的颜色集合'''
    colors = set()
    if axis == 0:
        for i in range(start, end):
            for j in range(grid.shape[1]):
                if grid[i, j] != -1:
                    colors.add(original_grid[i, j])
    else:
        for j in range(start, end):
            for i in range(grid.shape[0]):
                if grid[i, j] != -1:
                    colors.add(original_grid[i, j])
    return colors


def locked_candidates_elimination(grid: np.ndarray, original_grid: np.ndarray) -> tuple:
    '''锁定候选排除：如果连续 n 行/列只包含 n 种颜色，排除这些颜色在其他位置的出现'''
    rows, cols = grid.shape
    new_grid = grid.copy()
    changed = True
    
    while changed:
        changed = False
        
        for n in range(1, min(4, rows + 1)):
            for start in range(rows - n + 1):
                end = start + n
                colors = color_set_in_range(new_grid, original_grid, start, end, axis=0)
                
                if len(colors) == n:
                    for color in colors:
                        for i in range(rows):
                            if i < start or i >= end:
                                for j in range(cols):
                                    if new_grid[i, j] != -1 and original_grid[i, j] == color:
                                        new_grid[i, j] = -1
                                        changed = True
        
        for n in range(1, min(4, cols + 1)):
            for start in range(cols - n + 1):
                end = start + n
                colors = color_set_in_range(new_grid, original_grid, start, end, axis=1)
                
                if len(colors) == n:
                    for color in colors:
                        for j in range(cols):
                            if j < start or j >= end:
                                for i in range(rows):
                                    if new_grid[i, j] != -1 and original_grid[i, j] == color:
                                        new_grid[i, j] = -1
                                        changed = True
    
    if not row_detection(new_grid) or not col_detection(new_grid):
        return (False, new_grid)
    if not color_detection(new_grid, original_grid):
        return (False, new_grid)
    
    return (True, new_grid)


class CowSolver:
    def __init__(self, original_grid: np.ndarray):
        self.original_grid = original_grid.copy()
        self.rows, self.cols = original_grid.shape
        self.solutions = []
        self.required_colors = set(np.unique(original_grid))
    
    def backtrack(self, grid: np.ndarray, cows: list, used_colors: set, row: int = 0):
        '''回溯算法求解（带约束传播优化）'''
        # 锁定候选排除
        success, new_grid = locked_candidates_elimination(grid, self.original_grid)
        if not success:
            return
        grid = new_grid
        
        # 剪枝：检查约束条件
        if not row_detection(grid) or not col_detection(grid):
            return
        
        if not color_detection(grid, self.original_grid):
            return
        
        # 如果已经遍历完所有行
        if row >= self.rows:
            if len(cows) == self.rows and used_colors == self.required_colors:
                self.solutions.append(cows.copy())
            return
        
        # 找到当前行的有效位置
        valid_cols = []
        for col in range(self.cols):
            if grid[row, col] != -1:
                if is_valid_choice(grid, self.original_grid, row, col):
                    valid_cols.append(col)
        
        if not valid_cols:
            return
        
        # 最小剩余值启发式
        def get_future_options(col):
            temp_grid = fill_zero(row, col, grid)
            count = 0
            for r in range(row + 1, self.rows):
                count += sum(temp_grid[r, :] != -1)
            return count
        
        valid_cols.sort(key=get_future_options)
        
        for col in valid_cols:
            color = self.original_grid[row, col]
            temp_grid = fill_zero(row, col, grid)
            self.backtrack(temp_grid, cows + [(row, col)], used_colors | {color}, row + 1)
    
    def solve(self):
        '''求解并返回所有解'''
        self.solutions = []
        self.backtrack(self.original_grid.copy(), [], set(), 0)
        return self.solutions