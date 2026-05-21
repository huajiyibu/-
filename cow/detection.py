import numpy as np
def row_detection(grid:np.ndarray)->bool:
    size=grid.shape[0]
    for i in range(size):
        if grid[i,:].sum()==0:
            return False
    return True

def col_detection(grid:np.ndarray)->bool:
    size=grid.shape[0]
    for i in range(size):
        if grid[:,i].sum()==0:
            return False
    return True

def color_detection(d:dict):
    return  not (0 in d.values())

test_grid=[[0,1,1,1,1,1],
           [0,1,1,1,1,1],
           [0,1,1,1,1,1],
           [0,1,1,1,1,1],
           [0,1,1,1,1,1],
           [0,0,0,0,0,0]]
test_grid=np.array(test_grid)
print(col_detection(test_grid))


d={2:1,3:2,4:0}
print(color_detection(d))