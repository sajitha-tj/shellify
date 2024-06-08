import random
import threading
import time

class Mini_cli_animator:
    def __init__(self):
        self.frames = ['[▸] - ', '[▸] \ ', '[▸] | ', '[▸] / ']
        self.current_frame = 0
        self.current_thread = None
        self.current_thread_bool = False

    def animate_random_eq_bars(self, length: int):
        bar_heights = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        bars = [random.choice(bar_heights) for _ in range(length)]
        final_string = ''.join(bars)
        return final_string

    def animate(self):
        # print(self.frames[self.current_frame], end='\r')
        print("[▸] " + self.animate_random_eq_bars(30), end='\r')
        self.current_frame = (self.current_frame + 1) % len(self.frames)

    def animate_on_own_loop(self, delay_time: float = 0.5):
        while self.current_thread_bool:
            self.animate()
            time.sleep(delay_time)

    def animate_on_own(self, delay_time: float = 0.5):
        # animate on a separate thread
        self.current_thread_bool = True
        self.current_thread = threading.Thread(target=self.animate_on_own_loop, args=(delay_time,))
        self.current_thread.start()
        return self.current_thread

    def stop(self):
        self.current_thread_bool = False
        if self.current_thread:
            self.current_thread.join()
            self.current_thread = None
        print ("\033[A                             \033[A")