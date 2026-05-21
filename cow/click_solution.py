import pyautogui
import time
from operation import CowSolver
from grid_location import detect_grid


def click_cow_position(x, y, region, rows, cols):
    '''
    在指定的网格位置双击
    x: 网格行坐标（从0开始，0表示最下面一行）
    y: 网格列坐标（从0开始，0表示最左边一列）
    region: 屏幕区域 (x_offset, y_offset, width, height)
    rows: 网格行数
    cols: 网格列数
    '''
    x_offset, y_offset, width, height = region
    
    # 计算格子大小
    cell_width = width / cols
    cell_height = height / rows
    
    # 计算格子中心的屏幕坐标
    # 注意：网格坐标从左下角开始，屏幕坐标从左上角开始
    screen_x = x_offset + y * cell_width + cell_width / 2
    screen_y = y_offset + (rows - 1 - x) * cell_height + cell_height / 2
    
    # 移动鼠标到目标位置
    pyautogui.moveTo(screen_x, screen_y, duration=0.1)
    
    # 双击（0.2秒内点击两次）
    pyautogui.click()
    time.sleep(0.1)
    pyautogui.click()


def solve_and_click(image_path='img.jpg'):
    '''
    求解并点击答案
    '''
    # 定义屏幕区域（从screen_detect.py获取）
    region = (1095, 569, 885, 891)
    
    # 检测网格
    size, color_grid = detect_grid(image_path)
    cols, rows = size
    print(f'检测到网格: {cols}列 x {rows}行')
    
    # 求解
    solver = CowSolver(color_grid)
    solutions = solver.solve()
    
    if not solutions:
        print('没有找到解！')
        return
    
    # 使用第一个解
    solution = solutions[0]
    print(f'找到解，牛的位置: {solution}')
    
    # 等待用户准备
    print('请切换到游戏窗口，3秒后开始点击...')
    time.sleep(3)
    
    # 依次点击每个牛的位置
    for i, (x, y) in enumerate(solution):
        print(f'点击第 {i+1} 头牛: 网格位置({x}, {y})')
        click_cow_position(x, y, region, rows, cols)
        time.sleep(0.5)  # 点击间隔
    
    print('完成所有点击！')


if __name__ == '__main__':
    solve_and_click(r"C:\Users\huaji\Desktop\computer\AAAproject\cow\img.jpg")