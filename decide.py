#!/usr/bin/python

import random
import time

def gini(grouping, class_values):
    gini = 0.0

    # for each group
    for group in grouping:
        # for each class value
        size = float(len(group))
        if size == 0:
            continue
        for value in class_values:
            # count the number of that class value appearing in the group
            # and divide by the size of that group
            count = [row[-1] for row in group].count(value)
            prop = count/size
            gini += prop*(1-prop)

    return gini

def test_split(index, value, dataset):
    # pretty self explanatory
    left, right = [], []
    for row in dataset:
        if row[index] < value:
            left.append(row)
        else:
            right.append(row)
    return left, right

def best_split(dataset):
    # assuming the class value is always the last value in the row
    class_values = [row[-1] for row in dataset]
    b_index, b_score, b_value, b_groups = 999, 999, 999, None
    for row in dataset:
        for index,value in enumerate(row[:-1]):
            test_grouping = test_split(index, value, dataset)
            g_index = gini(test_grouping, class_values)
            if g_index < b_score:
                b_index, b_score, b_value, b_groups = index, g_index, \
                        value, test_grouping
    return {'index': b_index, 'value': b_value, 'groups': b_groups}

def terminate(group):
    outcomes = [row[-1] for row in group]
    return max(set(outcomes), key=outcomes.count)

def split(node, max_depth, min_size, depth):
    left, right = node['groups']
    del node['groups']

    # if the best split was a no-split
    if not left or not right:
        node['left'] = node['right'] = terminate(left + right)
        return

    # check for max_depth
    if depth >= max_depth:
        node['left'] = terminate(left)
        node['right'] = terminate(right)
        return

    # process left child
    if len(left) < min_size:
        node['left'] = terminate(left)

    else:
        node['left'] = best_split(left)
        split(node['left'], max_depth, min_size, depth+1)

    # process right child
    if len(right) < min_size:
        node['right'] = terminate(right)

    else:
        node['right'] = best_split(right)
        split(node['right'], max_depth, min_size, depth+1)

def build_tree(train, max_depth, min_size):
    root = best_split(train)
    split(root, max_depth, min_size, 1)
    return root

def guess(tree, row):
    cur = tree
    while 1:
        i = cur['index']
        v = cur['value']
        if row[i] < v:
            follow = cur['left']
        else:
            follow = cur['right']
        if isinstance(follow, dict):
            cur = follow
        else:
            return follow

if __name__ == '__main__':
    random.seed(0)

    # READ DATA
    with open('wine.data') as f:
        lines = f.readlines()

    dataset = []
    for line in lines:
        spl = line.split(',')
        assert len(spl) == 14

        # For wine
        row = [float(num) for num in spl[1:]]
        row.append(spl[0].strip())
        dataset.append(row)

    # BECAUSE WHY NOT
    random.shuffle(dataset) 

    cut = 100

    train = dataset[:cut]
    test = dataset[cut:]

    # TRAIN
    start = time.time()
    print "Training..."
    tree = build_tree(train, 5, 1)
    end = time.time()
    print "Training took %f seconds" % (end - start)

    # TEST
    print "Testing..."
    total = len(test)
    right = 0
    for row in test:
        g = guess(tree, row)
        if g == row[-1]:
            right += 1
    pct = round(float(right)*100/total,2)
    print "%.2f%%" % pct
