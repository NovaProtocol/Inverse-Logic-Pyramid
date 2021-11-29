import tkinter
import random
import itertools
import textwrap
import time
import typing


class Menu(tkinter.Frame):
    def __init__(self, root, *args, **kwargs):
        tkinter.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.process()
        self.done = False
        self.wins = 0

    def generate_truth_table(self, possible_operation):
        output = {}
        for operation in possible_operation.keys():
            for x, y in itertools.product([True, False], repeat=2):
                if operation in output:
                    result = possible_operation[operation](x, y)
                    if result in output[operation]:
                        output[operation][result].append((x, y))
                    else:
                        output[operation][result] = [(x, y)]
                else:
                    output[operation] = {}
        return output

    def check_operation_and_input(
        self,
        operation_lambda: dict,
        operation: typing.List[bool],
        input_data: typing.List[bool],
        expected_output: typing.List[bool],
    ) -> bool:
        for n, operation in enumerate(operation):
            if (
                operation_lambda[operation](input_data[n], input_data[n + 1])
                != expected_output[n]
            ):
                return False
        else:
            return True

    def generate_all_logic_combination(
        self,
        truth_table: dict,
        expected_output: typing.List[bool],
        operation_lambda: dict = None,
    ) -> typing.List[typing.List[bool]]:
        valid_combinations = []

        # non complicated for 1 element expected outcome
        if len(expected_output) == 1:
            for operation in truth_table.keys():
                for result in truth_table[operation].keys():
                    if result == expected_output[0]:
                        valid_combinations.append(
                            {
                                "operation": [operation],
                                "input": truth_table[operation][result],
                            }
                        )
            return valid_combinations

        # two or more items items in expected outcome
        else:
            ungrouped_valid_combinations = []
            for operations in itertools.product(
                truth_table.keys(), repeat=len(expected_output)
            ):
                for input_data in itertools.product(
                    [True, False], repeat=len(expected_output) + 1
                ):
                    if self.check_operation_and_input(
                        operation_lambda, operations, input_data, expected_output
                    ):
                        ungrouped_valid_combinations.append(
                            {
                                "operation": operations,
                                "input": [list(input_data)],
                            }
                        )
            for combination in ungrouped_valid_combinations:
                if combination["operation"] not in [
                    entry["operation"] for entry in valid_combinations
                ]:
                    valid_combinations.append(combination)
                else:
                    for entry in valid_combinations:
                        if entry["operation"] == combination["operation"]:
                            entry["input"].append(combination["input"])
            return valid_combinations

    def generate_game(
        self, levels: int = 5, hard: bool = True, final: bool = None, seed=None
    ):
        possible_operation = {
            "or": lambda x, y: x or y,
            "nor": lambda x, y: not (x or y),
            "and": lambda x, y: x and y,
            "nand": lambda x, y: not (x and y),
            "xor": lambda x, y: x ^ y,
            "xnor": lambda x, y: not (x ^ y),
        }

        possible_operation_list = ["or", "nor", "and", "nand"]

        # "XOR" and "XNOR" in case they want more challenge
        if hard:
            possible_operation_list.append("xor")
            possible_operation_list.append("xnor")

        # Pre-generate truth table
        truth_table = self.generate_truth_table(
            {
                operation: lambda_function
                for operation, lambda_function in possible_operation.items()
                if operation in possible_operation_list
            }
        )

        if not final:
            final = bool(random.randint(0, 1))

        if seed:
            random.seed(seed)

        while True:
            output = [[[], [final]]]
            for level_nth in range(levels - 1):
                operation_count = level_nth + 1
                target_output = output[level_nth][1]
                valid_entries = self.generate_all_logic_combination(
                    truth_table, target_output, possible_operation
                )
                if len(valid_entries) == 0:
                    # print("No valid entries found! Retrying...")
                    break
                chosen_operator = random.choice(
                    [entry["operation"] for entry in valid_entries]
                )
                chosen_input = random.choice(
                    *[
                        entry["input"]
                        for entry in valid_entries
                        if entry["operation"] == chosen_operator
                    ]
                )
                if type(chosen_input[0]) is list:
                    chosen_input = chosen_input[0]
                output.append([chosen_operator, chosen_input])
            else:
                break
        return output

    def generate_output(self, operation_list: list, input_list: list):
        possible_operation = {
            "or": lambda x, y: x or y,
            "nor": lambda x, y: not (x or y),
            "and": lambda x, y: x and y,
            "nand": lambda x, y: not (x and y),
            "xor": lambda x, y: x ^ y,
            "xnor": lambda x, y: not (x ^ y),
        }
        output_list = []
        for n, operation in enumerate(operation_list):
            output_list.append(
                possible_operation[operation](input_list[n], input_list[n + 1])
            )
        return output_list

    def help_ui(self):
        for item in self.winfo_children():
            item.destroy()
        help_message = (
            "This is a game where you are given a certain output and a table of logic operation. By only"
            "modifying the initial input, you need to get the given output with the least possible moves."
        )
        help_message = "\n".join(textwrap.wrap(help_message, width=38))
        title = tkinter.Label(
            self,
            text=f"Help",
            font=("Arial", 20),
            anchor=tkinter.N,
            bg="#808080",
            fg="#ffffff",
        )
        title.pack(pady=10)
        message = tkinter.Label(
            self,
            text=help_message,
            font=("Arial", 15),
            anchor=tkinter.CENTER,
            bg="#808080",
            fg="#ffffff",
        )
        message.pack(pady=10)

        back_btn = tkinter.Button(
            self,
            text="Back to Menu",
            font=("Arial", 10),
            command=self.main_ui,
            height=3,
            width=20,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        back_btn.pack(pady=5, anchor=tkinter.S)

    def number_only(self, entry):
        if entry.isdigit():
            return True
        else:
            return False

    def game_process(self):
        for item in self.winfo_children():
            item.destroy()
        if self.done:
            self.done = False
            self.start_game()

        def answer_button(answer):
            self.button_list[answer // 2] = not self.button_list[answer // 2]
            self.game_data[-1][1] = self.button_list
            for n, _ in enumerate(self.game_data[:-1]):
                self.game_data[-n - 2][1] = self.generate_output(
                    list(self.game_data[-n - 1][0]), list(self.game_data[-n - 1][1])
                )
            if self.answer == self.game_data[0][1][0] and not self.done:
                self.wins += 1
                self.done = True
                if self.auto_next:
                    self.game_process()
                else:
                    tkinter.Button(
                        self,
                        text="Next",
                        font=("Arial", 10),
                        command=self.game_process,
                        height=3,
                        width=20,
                        bg="#303030",
                        fg="#ffffff",
                        activebackground="#515151",
                        activeforeground="#aaffaa",
                    ).grid(
                        row=10,
                        column=0,
                        columnspan=self.current_val - 1,
                        pady=5,
                        sticky=tkinter.S,
                    )
                    time_taken = time.time() - self.start_time
                    timer = tkinter.Label(
                        self,
                        text=f"Time: {time_taken:.2f}s",
                        font=("Arial", 15),
                        bg="#555555",
                        fg="#ffffff",
                    )
                    timer.grid(
                        row=10,
                        column=(self.current_val * 2 - 1) - (self.current_val - 1),
                        columnspan=self.current_val - 1,
                        pady=10,
                    )

            if not self.done:
                self.game_process()

        title = tkinter.Label(
            self,
            text="Inverse Logic Pyramid",
            font=("Arial", 15),
            bg="#808080",
            fg="#ffffff",
        )
        title.grid(row=0, column=0, columnspan=self.current_val - 1, pady=10)
        win_rate = tkinter.Label(
            self,
            text=f"Wins: {self.wins}",
            font=("Arial", 15),
            bg="#808080",
            fg="#ffffff",
        )
        win_rate.grid(
            row=0,
            column=(self.current_val * 2 - 1) - (self.current_val - 1),
            columnspan=self.current_val - 1,
            pady=10,
        )

        for m, line in enumerate(self.game_data[::-1]):
            if m == 0:
                ref = [
                    val for pair in zip(line[1], tuple(line[0]) + ("",)) for val in pair
                ]
                for n, data in enumerate(ref):
                    if type(data) == bool:
                        btn = tkinter.Button(
                            self,
                            text=f"{int(self.button_list[n // 2]):^7}",
                            command=lambda n=n: answer_button(n),
                            font=("Arial", 12),
                            bg="#808080",
                            fg="#ffffff",
                            height=3,
                        )
                        btn.grid(row=m + 1, column=n + m)
                    else:
                        tkinter.Label(
                            self,
                            text=f"{data:^7}",
                            font=("Arial", 12),
                            bg="#808080",
                            fg="#ffffff",
                            height=3,
                        ).grid(row=m + 1, column=n + m)
            else:
                ref = [
                    val for pair in zip(line[1], tuple(line[0]) + ("",)) for val in pair
                ]
                for n, data in enumerate(ref):
                    tkinter.Label(
                        self,
                        text=f"{data if type(data) == str else data:^7}",
                        font=("Arial", 12),
                        bg="#808080",
                        fg="#ffffff",
                        height=3,
                    ).grid(row=m + 1, column=n + m)

    def start_game(self):
        for item in self.winfo_children():
            item.destroy()
        self.game_data = self.generate_game(
            levels=self.current_val, hard=self.current_xor
        )
        self.answer = self.game_data[0][1][0]
        self.grid_columnconfigure(tuple(range(self.current_val * 2 - 1)), weight=1)
        tries = 0
        while self.game_data[0][1][0] == self.answer:
            tries += 1
            self.button_list = [
                random.choice([True, False]) for x in range(self.current_val)
            ]
            self.game_data[-1][1] = self.button_list
            for n, _ in enumerate(self.game_data[:-1]):
                self.game_data[-n - 2][1] = self.generate_output(
                    list(self.game_data[-n - 1][0]), list(self.game_data[-n - 1][1])
                )
            if tries >= 50:
                print("Resetting")
                self.game_data = self.generate_game(
                    levels=self.current_val, hard=self.current_xor
                )
                self.answer = self.game_data[0][1][0]
                tries = 0
        self.start_time = time.time()
        self.game_process()

    def start_ui(self):
        for item in self.winfo_children():
            item.destroy()
        self.grid_columnconfigure(
            (
                0,
                1,
                2,
                3,
                4,
            ),
            weight=1,
        )

        title = tkinter.Label(
            self,
            text="Inverse Logic Pyramid",
            font=("Arial", 20),
            anchor=tkinter.N,
            bg="#808080",
            fg="#ffffff",
        )
        title.grid(row=0, column=0, columnspan=3, pady=10)

        self.current_val = 5

        def minus_btn_func():
            self.current_val -= 1
            current_count.config(text=str(self.current_val))
            if self.current_val < 2:
                self.current_val = 2
                current_count.config(text=str(self.current_val))

        def add_btn_func():
            self.current_val += 1
            current_count.config(text=str(self.current_val))
            if self.current_val > 6:
                self.current_val = 6
                current_count.config(text=str(self.current_val))

        info = tkinter.Label(
            self, text="Level:", font=("Arial", 15), bg="#808080", fg="#ffffff"
        )
        info.grid(row=1, column=0, columnspan=2)
        minus_button = tkinter.Button(
            self,
            text="-",
            font=("Arial", 10),
            command=minus_btn_func,
            height=3,
            width=self.winfo_width() // 60,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        minus_button.grid(row=1, column=2)
        current_count = tkinter.Label(
            self,
            text=5,
            font=("Arial", 20),
            width=self.winfo_width() // 60,
            height=2,
            bg="#999999",
            fg="#ffffff",
        )
        current_count.grid(row=1, column=3, pady=10)
        add_button = tkinter.Button(
            self,
            text="+",
            font=("Arial", 10),
            command=add_btn_func,
            height=3,
            width=self.winfo_width() // 60,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        add_button.grid(row=1, column=4)

        self.current_xor = False

        def toggle_xor_func():
            self.current_xor = not self.current_xor
            current_xor_label.configure(text=("Yes" if self.current_xor else "No"))

        info = tkinter.Label(
            self,
            text="Include XOR and XNOR:",
            font=("Arial", 15),
            bg="#808080",
            fg="#ffffff",
        )
        info.grid(row=2, column=0, columnspan=2)
        toggle_button = tkinter.Button(
            self,
            font=("Arial", 10),
            command=toggle_xor_func,
            height=3,
            width=self.winfo_width() // 60,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        toggle_button.grid(row=2, column=2)
        current_xor_label = tkinter.Label(
            self,
            text=str("No"),
            font=("Arial", 20),
            width=self.winfo_width() // 60,
            height=2,
            bg="#999999",
            fg="#ffffff",
        )
        current_xor_label.grid(row=2, column=3, pady=10, columnspan=2)

        blank_space_select = tkinter.Label(
            self,
            text=" ",
            font=("Arial", 20),
            width=self.winfo_width() // 60,
            height=2,
            bg="#808080",
        )
        blank_space_select.grid(row=9, column=3, pady=10, columnspan=2)

        self.auto_next = False

        def toggle_auto_next():
            self.auto_next = not self.auto_next
            current_auto_next_label.configure(text=("No" if self.auto_next else "Yes"))

        info = tkinter.Label(
            self,
            text="Display Time per level?:",
            font=("Arial", 15),
            bg="#808080",
            fg="#ffffff",
        )
        info.grid(row=3, column=0, columnspan=2)
        toggle_button_auto_next = tkinter.Button(
            self,
            font=("Arial", 10),
            command=toggle_auto_next,
            height=3,
            width=self.winfo_width() // 60,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        toggle_button_auto_next.grid(row=3, column=2)
        current_auto_next_label = tkinter.Label(
            self,
            text=str("Yes"),
            font=("Arial", 20),
            width=self.winfo_width() // 60,
            height=2,
            bg="#999999",
            fg="#ffffff",
        )
        current_auto_next_label.grid(row=3, column=3, pady=10, columnspan=2)

        blank_space_select = tkinter.Label(
            self,
            text=" ",
            font=("Arial", 20),
            width=self.winfo_width() // 60,
            height=2,
            bg="#808080",
        )
        blank_space_select.grid(row=9, column=3, pady=10, columnspan=2)

        back_btn = tkinter.Button(
            self,
            text="Back to Menu",
            font=("Arial", 10),
            command=self.main_ui,
            height=3,
            width=20,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        back_btn.grid(row=10, column=0, columnspan=2, pady=5, padx=5)
        go_btn = tkinter.Button(
            self,
            text="Start",
            font=("Arial", 10),
            command=self.start_game,
            height=3,
            width=20,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        go_btn.grid(row=10, column=3, columnspan=2, pady=5, padx=5)

    def main_ui(self):
        for item in self.winfo_children():
            item.destroy()
        test = tkinter.Label(
            self,
            text="Welcome to the Inverse Logic Pyramid!",
            font=("Arial", 25),
            anchor=tkinter.CENTER,
            bg="#808080",
            fg="#ffffff",
        )
        test.pack()

        test = tkinter.Label(
            self,
            text="Logic is the Key!",
            font=("Arial", 15),
            anchor=tkinter.CENTER,
            bg="#808080",
            fg="#ffffff",
        )
        test.pack(pady=10)

        start_btn = tkinter.Button(
            self,
            text="Start Game",
            font=("Arial", 10),
            command=self.start_ui,
            height=5,
            width=20,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        start_btn.pack(pady=1, anchor=tkinter.S)

        help_btn = tkinter.Button(
            self,
            text="Help",
            font=("Arial", 10),
            command=self.help_ui,
            height=5,
            width=20,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        help_btn.pack(pady=1, anchor=tkinter.S)

        exit_btn = tkinter.Button(
            self,
            text="Exit",
            font=("Arial", 10),
            command=self.quit,
            height=5,
            width=20,
            bg="#303030",
            fg="#ffffff",
            activebackground="#515151",
            activeforeground="#aaffaa",
        )
        exit_btn.pack(pady=1, anchor=tkinter.S)

    def process(self):
        self.root.title("Inverse Logic Pyramid")
        self.pack(fill=tkinter.BOTH, expand=1)
        self.configure(background="#808080")

        self.main_ui()


def main(root):
    Menu(root)
    root.mainloop()


if __name__ == "__main__":
    root = tkinter.Tk()
    root.geometry("600x600")
    root.title("MMW Project")
    main(root)
