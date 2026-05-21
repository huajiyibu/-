import pyautogui
import time
import random
from operation import CowSolver
from grid_location import detect_grid


def click_cow_position(x, y, region, rows, cols):
    '''
    在指定的网格位置双击（带随机误差）
    x: 网格行坐标（从0开始，0表示最下面一行）
    y: 网格列坐标（从0开始，0表示最左边一列）
    region: 屏幕区域 (x_offset, y_offset, width, height)
    rows: 网格行数
    cols: 网格列数
    '''
    x_offset, y_offset, width, height = region
    
    cell_width = width / cols
    cell_height = height / rows
    
    screen_x = x_offset + y * cell_width + cell_width / 2
    screen_y = y_offset + (rows - 1 - x) * cell_height + cell_height / 2
    
    screen_x += random.randint(-10, 10)
    screen_y += random.randint(-10, 10)
    
    pyautogui.moveTo(screen_x, screen_y, duration=0.5+random.uniform(-0.2,0.2))
    pyautogui.click()
    time.sleep(0.1+random.uniform(-0.01,0.01))
    pyautogui.click()


def main():
    '''
    主循环：截图→识别→解题→点击→等待5秒→循环
    '''
    region = (1082, 560, 912, 912)
    
    print('开始自动解题循环...')
    print('按 Ctrl+C 退出')
    i=0
    try:
        while True:
            i+=1
            print(f'\n=== 第 {i} 次循环 ===')
            
            # 1. 截图（不保存本地）
            print('正在截图...')
            screenshot = pyautogui.screenshot(region=region)
            
            # 2. 识别网格
            print('正在识别网格...')
            try:
                size, color_grid = detect_grid(screenshot)
                cols, rows = size
                print(f'检测到网格: {cols}列 x {rows}行')
            except Exception as e:
                print(f'识别失败: {e}')
                time.sleep(5)
                continue
            
            # 3. 解题
            print('正在解题...')
            solver = CowSolver(color_grid)
            solutions = solver.solve()
            
            if not solutions:
                print('没有找到解！')
                time.sleep(5)
                continue
            
            solution = solutions[0]
            print(f'找到解，牛的位置: {solution}')
            
            # 4. 依次点击每个牛的位置
            for i, (x, y) in enumerate(solution):
                print(f'点击第 {i+1} 头牛: 网格位置({x}, {y})')
                click_cow_position(x, y, region, rows, cols)
                
                sleep_time = 0.5 + random.uniform(-0.2, 0.2)
                time.sleep(sleep_time)
            
            # 5. 等待5秒后继续下一轮
            pyautogui.moveTo(100,100)
            print('等待5秒后继续...')
            time.sleep(5)
            
    except KeyboardInterrupt:
        print('\n用户中断，程序退出')


if __name__ == '__main__':
    main()