__author__ = 'wpl'

import urllib, json
from django.conf import settings

debug = False
if settings.DEBUG:
    debug = True



def unique_items(list):
    unique_list = []
    for item in list:
        if not item in unique_list:
            unique_list.append(item)
    return unique_list


def get_dict_in_list(key, value, dict_list):
    """
    Looks through a list of dictionaries and returns dict, where dict[key] == value
    """
    result = None
    for dict in dict_list:
        if dict[key] == value:
            result = dict
    return result


def get_branch_by_id(tree, id):
    """
    looks through a tree recursively for dict['id'] == id and returns the branch.
    Assumes that each branch item has a key, ['children'], that contains a list of dict objects in the same format as tree
    and another key, ['ascendants'], that is a string of ids starting with the dict object's top-level ancestor's id and
    each other ancestor ending with that dict object's id i.e
    tree =
    [
        {'id': 1,
        'ascendants': "1",
        'children': [
            {'id': 2,
            'ascendants': "1,2",
            'children': [
                {'id': 4,
                'ascendants': "1,2,4",
                'children': [
                    {'id': 5,
                    'ascendants': "1,2,4,5",
                    'children': [ ]
                    }
                }
                {'id': 3,
                'ascendants': "1,2,3",
                'children': [ ]
                }
            }
        },
        {'id': 6,
        'ascendants: "6",
        'children: []
        }
    ]
    """
    for branch in tree:
        if branch['id'] == id:
            return branch
        elif branch['children']:
            branch = get_branch_by_id(branch['children'], id)
            if branch:
                return branch


def get_used_branch_ids(p_tree):
    """
    p_tree = p['category_totals']
    returns list of branch ids and all of their ancestor ids, filters redundancies
    *NOTE: this is depending on the 'ascendants' method of task categories. If the 'ascendants' method isnt updating
    correctly, it is likely the cause of any issues with project summaries
    OK
    """
    used_object_ids = []
    for branch in p_tree:
        branch_ascendants = p_tree[branch]['ascendants'].split(',')
        branch_ascendants = [int(item) for item in branch_ascendants]
        used_object_ids.extend(branch_ascendants)
    used_object_ids = unique_items(used_object_ids)
    return used_object_ids


def create_used_item_list(tree, used_branch_ids):
    """
    using a list of ids, creates a list of branches with those ids
    NOTE: any modifications to branches should be done here or immediately after
    """
    branches = []
    for id in used_branch_ids:
        branch = get_branch_by_id(tree, id)
        branches.append(branch)
        if debug:
            print branch['id']
    for branch in branches:
        branch['children'] = []
    return branches


def modify_used_item_list(p_tree, used_item_list):
    """
    modify list of branches to include additional key, values
    """
    for item in used_item_list:
        task_set = []
        if p_tree.has_key(item['id']):
            for task in p_tree[item['id']]['task_set']:
                task_set.append(p_tree[item['id']]['task_set'][task])
                print task
                print p_tree[item['id']]['task_set'][task]
            item['task_set'] = task_set
            print task_set
            item['expense'] = p_tree[item['id']]['expense']
            item['price'] = p_tree[item['id']]['price']
            item['total'] = p_tree[item['id']]['total']
        else:
            item['task_set'] = []
            item['expense'] = 0
            item['price'] = 0
            item['total'] = 0
            print 'could not find target %d' % item['id']



def add_info_to_branch(tree, id, item):
    """
    adds item (branch) to a branch's children and increases price, expense, total of branch to include items values
    """
    target = None
    for branch in tree:
        if branch['id'] == id:
            target = branch
            if debug:
                print 'Found target, %d in first level' % id
            break
        elif branch['children']:
            if debug:
                print 'searching children for %d' % id
            target = get_branch_by_id(branch['children'], id)
            if target:
                break
    if target:
        if debug:
            print 'Appending %d to %d' % (item['id'], target['id'])
            print [child['id'] for child in target['children']]
        target['children'].append(item)
        target['price'] += item['price']
        target['expense'] += item['expense']
        target['total'] += item['total']
        if debug:
            print [child['id'] for child in target['children']]


def sort_tree(tree):
    tree = sorted(tree, key=lambda x: x['_order'])
    if debug:
        order = [(branch['id'], branch['_order']) for branch in tree]
        print order
    for branch in tree:
        if branch['children']:
            branch['children'] = sort_tree(branch['children'])
    return tree


def create_used_item_tree(used_item_list):
    """
    takes branches and organizes them into a recursive tree (or whatever this id called??)
    branches are modified with "add_info_to_branch" function
    """
    used_item_tree = []
    if debug:
        print [p_item['id'] for p_item in used_item_list]
        print [p_item['id'] for p_item in used_item_tree]
    for item in used_item_list[:]:
        if item['parent'] is None:

            if debug:
                print 'primary %d' % item['id']

            used_item_tree.append(item)
            used_item_list.remove(item)

    while len(used_item_list) is not 0:
        for item in used_item_list[:]:
            parent = get_dict_in_list('id', item['parent'], used_item_list)

            if debug:
                print '1. id: %d, parent: %d' % (item['id'], item['parent'])
                print [p_item['id'] for p_item in used_item_tree]

            if not parent:

                if debug:
                    print '2. %d' % item['id']
                    print [p_item['id'] for p_item in used_item_list]

                add_info_to_branch(used_item_tree, item['parent'], item)
                used_item_list.remove(item)

                if debug:
                    print '3. %d' % item['id']
                    print [p_item['id'] for p_item in used_item_list]

    return used_item_tree



