#!/usr/bin/env python
from __future__ import print_function
import sys, csv, random
from copy import deepcopy
from collections import OrderedDict

debug = True

def strequal(a, b):
    return a.casefold() == b.casefold()

def strinstr(a, b):
    return a.casefold() in b.casefold()

fields = ['Greek', 'Greek Romanized', 'Roman', 'Roman Anglicized', 'Etruscan', 'Egyptian', 'Description']
gods_dicts = []
for row in csv.DictReader(open('godinfos.csv', 'r'), delimiter='\t', fieldnames=fields, skipinitialspace=True):
    # replace empty fields with empty strings
    for key in row.keys():
        if row[key] is None:
            row[key] = ''
    gods_dicts.append(row)
used_gods = []

def read_csv_lines(filename, target_list, force_print_error=False):
    global debug
    try:
        for row in csv.reader(open(filename, 'r'), delimiter='\t'):
            # replace empty fields with empty strings
            for i, obj in enumerate(row):
                if obj is None:
                    row[i] = ''
            target_list.append(row)
    except Exception as err:
        print('Error reading %s: %s' % (filename, type(err)))
        if force_print_error or debug:
            print(err)


def read_lines(filename, target_list, force_print_error=False):
    global debug
    try:
        for row in open(filename, 'r').readlines():
            row_stripped = row.strip()
            if row_stripped != "":
                target_list.append(row)
    except Exception as err:
        print('Error reading %s: %s' % (filename, type(err)))
        if force_print_error or debug:
            print(err)


def find_god_dict(_name):
    global gods_dicts, fields
    for god in gods_dicts:
        name = _name.lower()
        for field in fields[:-1]: #exclude the description
            if strinstr(name, god[field]):
                return god
    return None


def generate_god_info_lines(god_dict):
    lines = ['Name: %s (%s)' % (god_dict['Greek Romanized'], god_dict['Greek']),
             # 'Roman: %s%s' % ("" if god_dict['Roman Anglicized'].strip() == "" else '%s / ' % god_dict['Roman Anglicized'], god_dict['Roman'])
             '']
    for field in fields[2:]:
        stripped_content = god_dict[field].strip()
        if stripped_content != "":
            lines.append('%s: %s' % (field, stripped_content))
    return lines


def print_god_info_text(god_name):
    god_dict = find_god_dict(god_name)
    if god_dict is None:
        print('No information available. :(')
        return
    lines = generate_god_info_lines(god_dict)
    print('\n'.join(lines))


def print_random_god():
    god_nr = random.randint(1, len(gods_dicts))
    print('Selecting random god #%i:' % god_nr)
    print('\n'.join(generate_god_info_lines(gods_dicts[god_nr - 1])))


def print_used_names(print_annotations):
    global used_gods
    if print_annotations:
        print('\nName\tAnnotation')
    for line in used_gods:
        print(line[0].strip() + ('\t' + ' '.join(line[1:]) if print_annotations else ''))
    return False


def find_available_names():
    global used_gods
    global gods_dicts
    to_check = deepcopy(used_gods)
    for god in gods_dicts:
        taken = False
        for i, used_god in enumerate(to_check):
            if used_god[0].lower() in god['Greek Romanized'].lower():
                taken = True
                #to_check.pop(i)
                break
        if not taken:
            yield god


def print_available_names():
    for god in find_available_names():
        print('"%s", "%s": %s' % (god['Greek Romanized'].strip(), god['Roman'].strip(), god['Description'].strip()))


def menu_edit_used_name_entry():
    pass


def print_actions(menu_name, actions):
    print('Menu "%s"\nAvailable actions:' % menu_name)
    print('Key\tDescription')
    print('---\t-----------')
    for action_key, action_parameters in actions.items():
        print(action_key + '\t' + action_parameters[0])
    return False


def show_menu(menu_name, actions, add_return_option=True, return_val=False):
    if debug:
        print('----------------------')
    actions_cpy = deepcopy(actions)
    actions_cpy['?'] = ('show this help', print_actions, [menu_name, actions_cpy])
    if add_return_option:
        actions_cpy['b'] = ('exit this menu', lambda b: b, [True])
    exit_menu = False
    # is not True to catch 'None' as well
    print('(%s) What would you like to do? Press "?" to show available actions' % menu_name)
    while exit_menu is not True:
        print('(%s) > ' % menu_name, end="")
        sys.stdout.flush()
        user_input = sys.stdin.readline().strip()
        if user_input not in actions_cpy:
            if user_input:
                print('(%s) unrecognised action, try again. Type ? for help' % menu_name)
                sys.stdout.flush()
        else:
            action = actions_cpy[user_input]
            exit_menu = action[1](*action[2])
            sys.stdout.flush()
    return return_val


def get_user_values(menu_name, values):
    # values should be a (dummy)-prefilled OrderedDict
    print('(%s) Please enter some information:' % menu_name)
    for key in values.keys:
        print('%s:' % key)
        values[key] = sys.stdin.readline().strip()
    print('done!')


def menu_confirm_values(menu_name, values, refresh_values_func, return_val=False):
    refresh_values_func(menu_name, values)
    print('(%s) Please confirm the following values:' % menu_name)
    for key, value in values.items():
        print('%s: %s' % (key, value))
    print('Are these values correct?')
    actions = OrderedDict(
        y=('yes', lambda b: b, [True]),  # FIXME follow up with actual data entry dialog
        n=('no, try again', menu_confirm_values, [menu_name, values, refresh_values_func, True])
    )
    show_menu(menu_name + '/Confirm', actions)
    return return_val


# menu declarations follow

def get_random_suggestion(menu_name, results):
    results.clear()
    available = list(find_available_names())
    god_nr = random.randint(1, len(available))
    if debug:
        print('Random suggestion: #%i out of %i available' % (god_nr, len(available)))
    # print('\n'.join(generate_god_info_lines(available[god_nr - 1])))
    for key, value in available[god_nr - 1].items():
        results[key] = value


PICK_NEW_NAME_ACTIONS = OrderedDict(
    #TODO: add 'insert new used name' dialog
    r=('get a random suggestion for a name', menu_confirm_values,
       ['random suggestion', OrderedDict(), get_random_suggestion, False])
)

EDIT_USED_NAME_ACTIONS = OrderedDict()


# end of menu declarations




def menu_main():
    actions = OrderedDict(
        u=('Print used names', print_used_names, [False]),
        p=('get used names + associated system info', print_used_names, [True]),
        a=('print available names', print_available_names, []),
        n=('pick a new name and add it to the use list', show_menu, ['Pick Name', PICK_NEW_NAME_ACTIONS]),
        e=('DUMMY edit or delete an entry in the used name list', show_menu, ['Edit Used', EDIT_USED_NAME_ACTIONS]),
        q=('quit', lambda a: a, [True])
    )
    show_menu('Main', actions, add_return_option=False)


if __name__ == '__main__':
    names = []
    if len(sys.argv) > 1:
        argument = sys.argv[1].strip()
        if len(argument) > 1:
            if argument.lower().endswith('.txt'):
                names = [line.strip() for line in open(sys.argv[1], 'r').readlines()]
            else:
                names = [argument]
            for name in names:
                stripped_name = name.strip()
                if stripped_name != "":
                    print('Input: %s' % stripped_name)
                    print_god_info_text(stripped_name)
        else:
            print('no proper argument given.'
                  'either input nothing, a single name or the path to a text file (name ending with .txt!) with names')
    else:
        read_csv_lines('used_names.csv', used_gods)

        menu_main()
