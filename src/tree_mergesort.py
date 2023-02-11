from math import floor

class Tree:
    """A tree for implementing mergeSort.  Every node contains a list and a flag to indicate if no more sorting is required."""
    def __init__(self, elts, left, right):
        """Requires that elts is either a singleton, in which case this is a leaf, or empty"""
        assert (len(elts) == 1 and left == None and right == None) or (len(elts) == 0)
        self.elts = elts
        self.right = right
        self.left = left
        self.complete = (len(elts) == 1)

class BadPath(Exception):
    """Path not found in tree."""
    pass

def string_of_tree (tree):
    """Renders trees as strings for readability.  A debug function.  Shouldn't be used in production."""
    if tree == None: return "||"
    return f"({string_of_tree(tree.left)} < {tree.elts} > {string_of_tree(tree.right)})"

def prepare(elts):
    """Transform an unsorted list into a tree.  Return a list of all paths through the tree to nodes which require sorting.  Paths are strings because they have to be passed through HTTP.  They only use "r" and "l"."""
    tree, paths, _last = prepare_recursive(list(enumerate(elts, 1)), "")
    return tree, paths

def prepare_recursive(elts, path):
    if len(elts) <= 1:
        return Tree(elts, None, None), [], True
    center = floor(len(elts) / 2)
    left, paths_left, left_last = prepare_recursive(elts[:center], path + "l")
    right, paths_right, right_last = prepare_recursive(elts[center:], path + "r")
    if left_last and right_last:
        final_paths = [path]
    else:
        final_paths = (paths_left if not left_last else []) + (paths_right if not right_last else [])

    return Tree([], left, right), final_paths, False

def decision(path, tree):
    """Recurse down the tree, following a path, and return the two unsorted elements at the end of it.  We validate the path as we go, as a bonus."""
    if path == "":
        return tree.left.elts[0], tree.right.elts[0]
    else:
        assert path[0] in ["l", "r"]
        return decision(path[1:], tree.left if path[0] == "l" else tree.right)

def update_tree(tree, passed, path, left_id, right_id, command, command_direction, max_pass):
    """
    Turn a user decision into a mergeSort step.
    
    The following commands are possible:
    * SORT (l|r): the chosen element is to be sorted higher than the other one.
    * STRIKE (l|r): the chosen element is to be deleted.
    * PASS (l|r): the chosen element has been unconditionally accepted and is to be promoted to the auto-pass list.

    After altering the tree, there will be a new comparison that has to be made.  Return a path to this comparison.
    """

    # Step 1: recurse down tree
    if len(path) > 0:
        new_path = update_tree(tree.left if path[0] == "l" else tree.right, passed, path[1:], left_id, right_id, command, command_direction, max_pass)
        if new_path == None:
            if tree.left.complete and tree.right.complete:
                return ""
            return None
        return path[0] + new_path
    
    # Step 2: verify ID
    if len(tree.left.elts) < 1 or tree.left.elts[0][0] != int(left_id) or len(tree.right.elts) < 1 or tree.right.elts[0][0] != int(right_id):
        raise BadPath

    # Step 3: carry out command
    subtree_elts = tree.left.elts if command_direction == "l" else tree.right.elts
    if command == "STRIKE":
        subtree_elts.pop(0)
    elif command == "PASS":
        passed.append(subtree_elts.pop(0))
    else:
        tree.elts.append(subtree_elts.pop(0))
    
    # Step 4: clean up empty sublists
    if len(subtree_elts) == 0:
        opposite_elts = tree.right.elts if command_direction == "l" else tree.left.elts
        tree.elts += opposite_elts
        tree.complete = True
    
    # Step 5: clean up overly-long sublists
    remaining_pass = max_pass - len(passed)
    if len(tree.elts) > remaining_pass:
        tree.elts = tree.elts[:remaining_pass]
    if len(tree.elts) == remaining_pass:
        tree.complete = True

    # Step 6: return
    if tree.complete:
        return None
    return ""
         