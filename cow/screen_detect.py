import pyautogui
def image():
    region=(1095,569,885,891)
    img=pyautogui.screenshot(region=region)
    return img
image().save('img.jpg')