import requests

from logging import getLogger
from desktop_controller import (BotcityController, PyAutoGuiController,
                                NotepadTestHelperFuncs, is_task_running)


logger = getLogger("desktop-data-entry")


class NotepadBotCity(BotcityController, NotepadTestHelperFuncs):
    def __init__(self):
        super().__init__()
        self.file_count = 10
    
    def open_notepad(self):
        self.logger.info("Opening Notepad")
        self.current_process = self.open_app('C:\\Windows\\notepad.exe')


class NotepadPyautogui(PyAutoGuiController, NotepadTestHelperFuncs):
    def __init__(self):
        super().__init__()
        self.file_count = 10
        self.app_name = 'notepad.exe'

    def open_notepad(self):
        self.open_app(self.app_name)
        if not is_task_running(self.app_name):
            self.raise_for_prompts()
            err = f'Failed to open `{self.app_name}`...'
            confirm = self.wait_for_user(f'{err}\nPress continue to retry, or Cancel to quit.')
            if confirm:
                self.open_notepad()
            raise Exception(f'{err} User aborted.')

def main():
    bot = NotepadPyautogui()
    # bot = NotepadBotCity()
    
    try:
        posts = get_posts(count=bot.file_count)
        for post in posts:
            pid, title, body = parse_post(post)
            filename = f'post {pid}.txt'
            bot.open_notepad()
            bot.type_and_save(filename=filename, content=f"TITLE: {title}\n\nBODY:\n{body}")
            bot.close_notepad()
    except Exception as e:
        bot.logger.error(f"An error occurred", exc_info=True)
    finally:
        if process := getattr(bot, 'current_process', None):
            bot.terminate_process(process)


def get_posts(count=10):
    url = f"https://jsonplaceholder.typicode.com/posts?_limit={count}"
    response = requests.get(url)
    if response.status_code == 200:
        posts = response.json()
    else:
        logger.info(f"Failed to retrieve posts. Status code: {response.status_code}")
        posts = None
    return posts

def parse_post(post_data):
    try:
        pid = post_data['id']
        title = post_data['title']
        body = post_data['body']
    except Exception:
        logger.error("Error parsing post", exc_info=True)
        pid = title = body = None
    return pid, title, body

if __name__ == "__main__":
    main()
