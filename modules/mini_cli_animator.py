import random
import threading
import time

class Mini_cli_animator:
    def __init__(self):
        self.frames = ['[▸] - ', '[▸] \ ', '[▸] | ', '[▸] / ']
        self.current_frame = 0
        self.current_thread = None
        self.current_thread_bool = False

    def generate_random_eq_bars(self, length: int):
        bar_heights = ['▁', '▂', '▃', '▄', '▅', '▆', '▇'] #, '█'
        bars = [random.choice(bar_heights) for _ in range(length)]
        final_string = ''.join(bars)
        return final_string

    def animate(self):
        # print(self.frames[self.current_frame], end='\r')
        print("[▸] " + self.generate_random_eq_bars(30))
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
        print ("\033[A                                                                           \033[A")

    def animate_long_text(self, text: str, current_index:int, display_length: int = 20, fixed_prefix: str = "", fixed_suffix:str = ""):
        seperating_white_spaces_length = int(display_length / 2)
        # current index is returned to 0 if it exceeds length of text + half of display length(which is the length of white space seperator)
        if (current_index >= (len(text) + seperating_white_spaces_length)):
            current_index = 0
        starting_point = current_index

        if starting_point > len(text): # starting point > length of text means, current loop has ended. so we print spaces and the remaining part of the text from next loop
            printable_text = ""
            no_of_spaces_in_end = seperating_white_spaces_length - (current_index - len(text)) # no of spaces = (total no of spaces) - (offset from text of current loop)
            no_of_chars_for_next_loop = display_length - no_of_spaces_in_end
            next_loop_text = text[0:no_of_chars_for_next_loop]
        else: # normal functions. prints part of current loop, spaces and part of next loop if possible [ex: fgh     abcde]
            # calculating ending position
            ending_point = current_index+display_length
            no_of_spaces_in_end = 0
            if(ending_point > len(text)):
                no_of_spaces_in_end = ending_point - len(text) # spaces are printed to clear the terminal and to seperate next loop
                ending_point = len(text)
            # text to print from the current loop
            printable_text = text[starting_point: ending_point]
            # next loop text logic
            no_of_chars_for_next_loop = 0
            next_loop_text = ""
            if no_of_spaces_in_end > seperating_white_spaces_length:
                no_of_chars_for_next_loop = no_of_spaces_in_end - seperating_white_spaces_length
                no_of_spaces_in_end = seperating_white_spaces_length
                next_loop_text = text[0:no_of_chars_for_next_loop]
        # final string has 3 parts: part of text from current loop(printable_text), spaces, part of text from current loop(next_loop_text)
        print(fixed_prefix + printable_text + (" " * no_of_spaces_in_end) + next_loop_text + fixed_suffix)
        return current_index+1

if __name__ == '__main__':
    anim = Mini_cli_animator()
    i=0
    for j in range(50):
        i = anim.animate_long_text("abcdefghijklmnopqrstuvwxyz",current_index=i, display_length=10)
        time.sleep(0.1)
        print(f"\033[A", end='\r')
