from contextlib import suppress
import os
import atexit
import signal
import pyautogui
import subprocess

from time import sleep as time_sleep
from botcity.core import DesktopBot
from logging import getLogger, basicConfig, DEBUG
from collections import namedtuple
from PIL import Image
from pathlib import Path


ScreenBox = namedtuple("ScreenBox", ["left", "top", "width", "height"])
BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"

def get_template_path(label):
    return RESOURCES_DIR / f"{label}.jpg"

def sanitize_image(image_path):
    """Re-save image to a format that OpenCV and pyautogui can always read."""
    try:
        with Image.open(image_path) as img:
            rgb_img = img.convert('RGB')  # convert to RGB just in case
            rgb_img.save(image_path, format='JPEG')  # overwrite safely
            print(f"✅ Sanitized image: {image_path}")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to sanitize image: {e}")


def is_task_running(task='notepad.exe'):
    output = os.popen(f'tasklist /FI "IMAGENAME eq {task}"').read()
    return task in output

# this is an optional Controller using botcity
class BotcityController(DesktopBot):
    basicConfig(
            level=DEBUG, format='[Desktop Controller] %(asctime)s - %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )

    def __init__(self, *args, **kwargs):
        self.logger = getLogger(__name__)
        self.logger.info("Initializing Desktop Controller")
        super().__init__(*args, **kwargs)
    # apps = {'notepad': 'C:\\Windows\\notepad.exe'}

    def open_app(self, app_path, wait=True):
        """Launch an application."""
        self.execute(app_path)
        process = self.find_process(app_path.split("\\")[-1])
        for i in range(5):
            if wait:
                self.sleep(1000 + i * 1000)
            if process.status() == 'running':
                self.logger.info(f"Application {app_path} is running.")
                return process
            self.logger.info(f"App `{app_path}` not started yet...")
        else:
            self.logger.error(f"App `{app_path}` failed to start.")
            return None
    
    def press(self, key):
        if key := getattr(self, key, None):
            key()
        else:
            self.logger.error(f"Key `{key}` not found... action not performed.")


class PyAutoGuiController:
    def __init__(self):
        self.logger = getLogger(__name__)
        self.logger.info("Initializing PyAutoGui Controller")
        self.processes = []
        atexit.register(self.cleanup)
        pyautogui.FAILSAFE = True
        self.badges = {
            "error-badge": True,
            "warning-badge": True,
        }
    def sleep(self, seconds):
        time_sleep(seconds)

    def open_app(self, executable_path):
        '''
        Launch an application via subprocess and track it for cleanup.
        '''
        self.logger.info(f"Launching application: {executable_path}")
        try:
            self.current_process = proc = subprocess.Popen(executable_path)
            self.processes.append(proc)
            self.sleep(1)
            if proc.poll() is None:
                self.logger.info(f'`{executable_path}` is running (PID={proc.pid}).')
            else:
                raise Exception(f'`{executable_path}` exited immediately.')
        except Exception as e:
            raise RuntimeError(f"Failed to open `{executable_path}`: {e}")

    def find(self, label, matching=0.8, *args, **kwargs):
        """
        Locate the image on the screen and return its box. Raises if not found and flag is set.
        """
        image_path = get_template_path(label)
        self.logger.debug(f"🔍 Looking for image: {image_path}")

        try:
            matched = pyautogui.locateOnScreen(str(image_path), confidence=matching)
        except OSError:
            self.logger.warning(f"⚠️ Cannot read image. Attempting to sanitize: {image_path}")
            sanitize_image(image_path)
            matched = pyautogui.locateOnScreen(str(image_path), confidence=matching)

        if matched:
            box = ScreenBox(*matched)
            self.logger.debug(f"✅ Found at: {box}")
            return box
        else:
            self.logger.warning(f"❌ Image not found: {image_path}")
            return None

    def save_notepad(self, *args, **kwargs):
        super().save_notepad(*args, **kwargs)
        self.sleep(1)
        if not (found := self.check_for_prompts()):
            return
        res = self.wait_for_user(f"An unexpected prompt was found.\n\n{found}\n\nPress Retry to try again, Ignore to skip, or Cancel to abort.")
        match res:
            case "Retry":
                for i in range(3):
                    self.press("escape")
                self.save_notepad(*args, **kwargs)  # Recursive call
            case 'Ignore':
                self.logger.info("Ignoring...")
                self.badges.update({found: False})
            case 'Cancel':
                self.logger.info("User aborted.")
                quit()

    def check_for_prompts(self):
        for badge, check in self.badges.items():
            if not check:
                continue
            location = None
            with suppress(Exception):
                location = self.find(badge, matching=0.8)
            if location:
                return badge

    def wait_for_user(self, msg):
        response = pyautogui.confirm(text=msg, title='Confirmation', buttons=['Retry', 'Ignore', 'Cancel'])
        return response

    def click_at(self, x, y):
        pyautogui.click(x=x, y=y)

    def kb_type(self, text, interval=0):
        pyautogui.typewrite(text, interval=interval * .25)

    def tab(self):
        pyautogui.press('tab')

    def press(self, key):
        pyautogui.press(key)

    def hold(self, key):
        pyautogui.keyDown(key)

    def release(self, key):
        pyautogui.keyUp(key)

    def type_keys(self, keys: list):
        pyautogui.hotkey(*keys)

    def cleanup(self):
        self.logger.info("Cleaning up launched processes...")
        for proc in self.processes:
            if proc.poll() is None:  # Still running
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                    self.logger.info(f"Terminated PID {proc.pid}")
                except Exception as e:
                    self.logger.warning(f"Error terminating PID {proc.pid}: {e}")
        self.processes.clear()

    def terminate_process(self, process):
        self.logger.info(f"Terminating process: {process.pid}")
        if process.poll() is None:
            process.terminate()

class NotepadTestHelperFuncs:
    '''
    Any helper funcs to be used by other classes should be added here
    This class is used to 'unify' testing between botcity and pyautogui
    to avoid writing different funcs for each one.
    '''
    def type_and_save(self, content, filename):
        self.logger.info("Typing content into Notepad")
        self.kb_type(content, 0.1)
        self.sleep(0.5)
        self.save_notepad(filename)

    def save_notepad(self, filename):
        # Check if the directory Desktop\tjm-project exists, if not create it
        desktop_path = Path.home() / "Desktop" / "tjm-project"
        if not desktop_path.exists():
            self.logger.info(f"Directory {desktop_path} does not exist. Creating it.")
            desktop_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Saving file {filename}")
        self.type_keys(['ctrl', 'shift', 's'])
        self.sleep(0.5)
        self.kb_type(filename, 0.1)
        self.press('space')
        self.press('backspace')
        # check for the images/path-bar.jpg on screen and click on it
        img = 'path-bar'
        if el := self.find(label=img, matching=0.8):
            x, y = self.get_centered_coords(el)
            self.click_at(x=x, y=y)
            # type the path `Desktop`
            self.kb_type(str(desktop_path), 0.1)
            self.press('enter')
            self.sleep(0.5)
            self.type_keys(['alt', 's'])
        else:
            raise Exception(f"Image '{img}.jpg' not found on screen")
    
    def get_centered_coords(self, box):
        return (box.left + box.width // 2), (box.top + box.height // 2)

    def close_notepad(self):
        self.current_process.terminate()
