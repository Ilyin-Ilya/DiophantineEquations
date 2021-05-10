import random
import copy

import PySimpleGUI as sg
from typing import Tuple, List


class foundAnswer(Exception):
    """Raised when the input value is too small"""
    pass


def print_hi(name):
    general_info = [[sg.Text('Diophantine equation')],
                    [sg.Text('Enter number of params'), sg.InputText(key="-number_of_params-")],
                    [sg.Button("Build equation model", key="-build_model-")]]
    # Create the window
    window = sg.Window("Demo", general_info, margins=(400, 300))

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == sg.WIN_CLOSED:
            break
        if event == "-build_model-":
            number_of_params = (int)(values['-number_of_params-'])
            model = build_model(number_of_params)
            model.append([sg.Button("Solve the equation", key="-solver-")])
            window1 = sg.Window("Diophantine equation", model, margins=(400, 300))
            window.Close()
            window = window1
        if event == "-solver-":
            eq = scan_equation(number_of_params, values)
            first_pop = generate_first_population(eq)
            for i in range(number_of_params*eq[1]*eq[1]):
                try:
                    inaccuracy = calculate_population_inaccuracy(eq, first_pop)
                    children = crossing(first_pop, inaccuracy)
                    replace_old_with_new(first_pop, children, inaccuracy, eq)
                    mutate(first_pop, eq[1])
                except foundAnswer as ex:
                    res_set = ex.args[0]
                    res=get_answer(res_set,eq)
                    res.append([sg.Text("generation: " + str(i))])
                    window1 = sg.Window("Diophantine equation", res, margins=(400, 300))
                    window.Close()
                    window = window1
                    break
            if i == number_of_params*eq[1]*eq[1]-1:
                sg.popup("No result")
    window.close()


def build_model(number_of_elems: int):
    model = [[]]
    i = 0
    for i in range(0, number_of_elems - 1):
        model[0].extend([sg.InputText(key="-coef_" + str(i) + "-", size=(5, 5)), sg.Text('a_' + str(i) + ' +')])
    model[0].extend([sg.InputText(key="-coef_" + str(i + 1) + "-", size=(5, 5)), sg.Text('a_' + str(i + 1) + ' =')])
    model[0].extend([sg.InputText(key="-value-", size=(5, 5))])

    return model


def scan_equation(number_of_params: int, values: dict) -> Tuple[List[int], int]:
    equation = []
    for i in range(0, number_of_params):
        if number_of_params==1:
            equation.append(int(values["-coef_" + str(i+1) + "-"]))
            break
        equation.append(int(values["-coef_" + str(i) + "-"]))
    pair = (equation, (int)(values["-value-"]))
    return pair

1
def generate_first_population(equation: Tuple[List[int], int]) -> List[List[int]]:
    population_amount = 10;
    population = []
    for i in range(population_amount):
        population_set = []
        for j in range(len(equation[0])):
            population_set.append(random.randint(0, equation[1]))
        population.append(population_set)
    return population


def calculate_inaccuracy(equation: Tuple[List[int], int], population_member: List[int]) -> int:
    equation_sum = 0
    for i in range(len(equation[0])):
        equation_sum += equation[0][i] * population_member[i]
    res = abs(equation_sum - equation[1])
    if res == 0:
        raise foundAnswer("Found answer")
    return res

def get_answer(result_set:List[int], equation: Tuple[List[int], int]):
    model = [[]]
    i=0
    for i in range(0, len(result_set) - 1):
        model[0].extend([sg.Text(str(equation[0][i]) + '*' + str(result_set[i]) + ' +')])
    if len(result_set)==1:
        model[0] = [sg.Text(str(equation[0][i]) + '*' + str(result_set[i]) + '=')]
    else:
        model[0].extend([sg.Text(str(equation[0][i+1]) + '*' + str(result_set[i + 1]) + ' =')])
    model[0].extend([sg.Text(str(equation[1]))])
    return model

def calculate_population_inaccuracy(equation: Tuple[List[int], int], population: List[List[int]]) -> List[int]:
    population_inaccuracy = []
    for i in population:
        try:
            population_inaccuracy.append(calculate_inaccuracy(equation, i))
        except foundAnswer:
            raise foundAnswer(i)
    return population_inaccuracy


"list of pairs with numbers"


def select_parents(innacuracy: List[int], population_amount: int) -> List[Tuple[int, int]]:
    res = []
    s1 = []
    for i in range(0, population_amount):
        s1.append(i)

    g = random.choices(s1, calculate_probabilities(innacuracy), k=int((population_amount)))
    for i in range(0, population_amount, 2):
        res.append((g[i], g[i + 1]))
    return res


def calculate_probabilities(innacuracy: List[int]) -> List[float]:
    sum = 0
    for i in range(len(innacuracy)):
        sum += innacuracy[i]
    res = []
    for i in range(len(innacuracy)):
        res.append(1 - innacuracy[i] / sum)
    return res


def cross_parents(parent1: List[int], parent2: List[int]) -> List[int]:
    son = []
    i = 0
    while i < len(parent1):
        if i < len(parent1) / 2:
            son.append(parent1[i])
        else:
            son.append(parent2[i])
        i += 1
    return son


def crossing(population: List[List[int]], innacuracies: List[int]) -> List[List[int]]:
    parents = select_parents(innacuracies, len(population))
    res = []
    for i in parents:
        res.append(cross_parents(population[i[0]], population[i[1]]))
    return res


def replace_old_with_new(parents: List[List[int]], children: List[List[int]], innacuracies: List[int],
                         equation: Tuple[List[int], int]) -> List[List[int]]:
    innacuracies.sort(reverse=True)
    i = 0
    parents_copy=copy.deepcopy(parents)
    while i < len(children):
        for j in range(0,len(parents_copy)):
            if calculate_inaccuracy(equation, parents_copy[j]) == innacuracies[i]:
                parents[j] = children[i]
                i += 1
                break
    return parents


def mutate(population: List[List[int]], equation_value: int):
    pop_num = random.randint(0, len(population) - 1)
    param_num = random.randint(0, (len(population[0])-1))
    new_number = random.randint(0, equation_value)
    population[pop_num][param_num] = new_number


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
