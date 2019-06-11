#--------------------------------------------------
# CONSTANTS
#--------------------------------------------------

# These are of the following format:
# OPERATOR = (tuple of single chars that can be translated into the operator)
# Space is included just to ease validity checking and translation.

AND = ('^', '&', '+',)
OR = ('v', '/',)
IF = ('>',)
IFF = ('=',)
NOT = ('~', '-', '!')
LEFT = ('(',)
RIGHT = (')',)
SPACE = (' ',)

# For the purposes of validity checking, also make tuples of all possible input.

ALL_SYMBOLS = (AND + OR + IF + IFF + NOT + LEFT + RIGHT + SPACE)
ALL_NAMES = ('P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',)

# During translation, this dictionary will be used to turn input into Python.

SYMBOL_TO_PYTHON = {
    AND: ' and ',
    OR: ' or ',
    IF: ' is False or ',
    IFF: ' is ',
    NOT: ' not ',
    LEFT: ' ( ',
    RIGHT: ' ) ',
    SPACE: ' '
    }

# During validity checking, this dictionary converts a code to a message.

ERROR_TO_MESSAGE = {
    1: 'invalid character',
    2: 'improper brackets',
    3: 'faulty syntax'
    }

#--------------------------------------------------
# WORLD GENERATION
#--------------------------------------------------

def get_worlds(names):
    
    if names == []:
        return [{}]
    
    smaller = get_worlds(names[:len(names)-1])
    bigger = []
    
    for world in smaller:
        plus_True = world.copy()
        plus_False = world.copy()
        
        plus_True.update({names[len(names)-1]: True})
        plus_False.update({names[len(names)-1]: False})
        
        bigger.append(plus_True)
        bigger.append(plus_False)
    
    return bigger


def get_dummy_world(names):
    '''
    Return a single dictionary in which every name has the value True
    for the purposes of validating the syntax.
    '''
    
    world = {}
    
    for name in names:
        world[name] = True
        
    return world


#--------------------------------------------------
# LOGIC EVALUATION
#--------------------------------------------------
   
def evaluate_world(premises, conclusion, world):
    '''
    Take a single world and test the argument.
    Return a tuple of three bools: the first represents whether the argument is
    valid, the second whether the premises were true, the third whether the
    conclusion was true.
    '''
    
    # Default values for whether it passes and whether the premises are true.
    
    valid = True
    premises_true = False
    conclusion_true = eval(conclusion)
    
    # Unify the premises in order to simplify evaluating them all at once.
    
    if not premises:
        premises_true = True
        valid = conclusion_true
    
    else:
        unified_premises = ''
        for premise in premises:
            unified_premises += '({}) and '.format(premise)  
    
        # Truncate the last ' and ' ...
        
        unified_premises = unified_premises[:-5]
        
        if eval(unified_premises):
            valid = conclusion_true
            premises_true = True
    
    return valid, premises_true, conclusion_true
        

def evaluate_argument(premises, conclusion, names):
    '''
    Take a list of premises, a conclusion string, and a list of names.
    Get the worlds for them. Then iterate through every world. If any world is
    evaluated False, the argument is invalid. Otherwise it is valid.
    Return a tuple consisting of:
    1. a bool denoting the validity of the argument
    2. a counterexample world
    3. a bool denoting whether the premises were ever true
    4. a bool denoting whether the conclusion was ever true
    5. a bool denoting whether the conclusion was always true
    '''
    
    always_valid = True
    premises_ever_true = False
    conclusion_ever_true = False
    conclusion_always_true = True
    counterexample = {}
    
    worlds = get_worlds(names)
    
    for world in worlds:
        
        valid, premises_true, conclusion_true = evaluate_world(premises,
                                                               conclusion,
                                                               world)
        if not valid:
            counterexample = world
        
        always_valid = min(always_valid, valid)
        premises_ever_true = max(premises_ever_true, premises_true)
        conclusion_ever_true = max(conclusion_ever_true, conclusion_true)
        conclusion_always_true = min(conclusion_always_true, conclusion_true)
            
    return always_valid, counterexample, premises_ever_true,\
           conclusion_ever_true, conclusion_always_true


#--------------------------------------------------
# INPUT CLEANUP AND TRANSLATION
#--------------------------------------------------

def translate(string):
    '''
    string is the string to be translated into Python. It gets translated by
    converting all symbols to Python logic, taking a list of names, and then
    replacing each name with "world[name]".
    
    Return the translation and the list of names used therein.
    '''
    
    translation = ''
    names = []
        
    for char in string:
        
        if char in ALL_SYMBOLS:
            
            # The method for symbols is to find which operator it falls under
            # and translate it to the string that operator translates to.
            
            for symbol in SYMBOL_TO_PYTHON:
                
                if char in symbol:
                    translation += SYMBOL_TO_PYTHON[symbol]
                    break
        
        # The method for names is to add its reference to the list of names
        # and insert ' world["name"] ' in the translation.
        
        elif char in ALL_NAMES:
            names.append(char)
            translation += ' world["{}"] '.format(char)
    
    # We padded spaces around every piece of the translation in case the user
    # forgot any. Now remove all double spaces.
    
    while '  ' in translation:
        translation = translation.replace('  ', ' ')
    
    # And trailing whitespace...
    
    translation = translation.strip()
    
    return translation, names


def translate_all(premises, conclusion):
    '''
    Given a list of premise strings and a conclusion string, return a list of
    translated premise strings, a translated conclusion string, and a list of
    names used in all of them.
    '''
    
    all_names = []
    translated_premises = []
    
    for premise in premises:
        translation, names = translate(premise)
        translated_premises.append(translation)
        all_names.extend(names)
        
    translation, names = translate(conclusion)
    translated_conclusion = translation
    all_names.extend(names)
    
    # Remove duplicates from the names list by converting to and from a set.
    
    all_names = list(set(all_names))
    
    return translated_premises, translated_conclusion, all_names


def clean_input(premises, conclusion):
    '''
    Take two strings (raw input from text fields). Return a list of strings for
    premises (leaving out empty strings) and a string for the conclusion.
    '''
    
    premises = premises.split('\n')
    premises_clean = []
    
    for premise in premises:
        premise = premise.strip()
        if premise:
            premises_clean.append(premise)
            
    conclusion_clean = conclusion.strip()
    
    return premises_clean, conclusion_clean


#--------------------------------------------------
# INPUT VALIDITY AND CIRCULARITY CHECKING
#--------------------------------------------------

def get_bracket_subsegment(string):
    '''
    string begins at the index right after a bracket. A closing bracket is
    guaranteed. Return the subsegment of the string that consists of all the
    material in this unit (excluding any internal bracket units).
    '''
       
    sub = ''
    depth = 1
    
    i = 0
    while i < len(string):
        
        # Check if we're beginning a nested bracket unit.
        
        depth += string[i] == '('
        
        # Only add to the subsegment if we are back at the main unit level.
            
        if depth == 1:
            sub += string[i]
            
        # Check if we're exiting a nested bracket unit.
            
        depth -= string[i] == ')'
        
        # Check if we just exited the main unit level.
        
        if depth == 0:
            break
        
        i += 1
            
    return sub[:-1] # Slice off the closing bracket of the main unit level.


def good_brackets(string):
    '''
    Go through each bracket unit in a string. Return False iff any subsegment
    is empty after stripping or there is a mismatch in the number of brackets.
    '''
    
    # Equal number of brackets.
    
    if string.count('(') != string.count(')'):
        return False
        
    i = 0
    while i < len(string):
        
        string = string[i:]
        bracket_start = string.find('(')
                
        # Do we have any units left?
                        
        if bracket_start == -1:
            break
        
        # Get the subsegment of this bracket.
        
        bracket_sub = get_bracket_subsegment(string[bracket_start + 1:])
        
        # Ensure it is not empty.
        
        if not bracket_sub.strip():
            return False
        
        i += 1
            
    return True


def is_valid(string):
    '''
    There are three validity checks for this string, using these error codes:
    1. It contains only our predefined sentential logic.
    2. It contains at least one name.
    3. It is evaluable by Python.
    Return a tuple where the first value is a bool for whether it passed all
    the tests and the second is None or the error code of the failed test.
    '''
    
    # First test
    
    for char in string:
        if not (char in ALL_NAMES or char in ALL_SYMBOLS):
            return False, 1
        
    # Second test
    
    if not good_brackets(string):
        return False, 2
    
    # Third test
    
    translation, names = translate(string)
    world = get_dummy_world(names)
    
    try:
        bool(eval(translation))
        return True, None
    except:
        return False, 3
    
    
def is_circular(premises, conclusion):
    '''
    premises is a list of strings and conclusion is a string.
    Test if the conclusion appears in any form in the premises.
    Return True iff it does.
    '''
    
    if not premises:
        return False
        
    # Strip conclusion down until it has no brackets that could make it look
    # like it was not identical to a premise.
    
    while conclusion.startswith('(') and conclusion.endswith(')'):
        conclusion = conclusion[1:-1]
        conclusion = conclusion.strip()
        
    # But the premises could also have brackets. Rather than strip each one
    # down, we'll just add brackets to the conclusion. First establish the
    # length of the longest premise so we know when to stop adding brackets.
    
    enough = len(max(premises, key=len))
    
    while len(conclusion) <= enough:
        
        if conclusion in premises:
            return True
        
        conclusion = '( {} )'.format(conclusion)
    
    return False


#--------------------------------------------------
# INTERFACE
#--------------------------------------------------

def get_result_text(raw_premises, raw_conclusion):
    '''
    premises and conclusion are strings that come directly from the text fields.
    
    Return a tuple of two strings. The first summarizes the evaluation of the
    argument (None, Error, Valid, Invalid), and the second gives some detail
    of the analysis.
    '''
    
    # Short-circuit: check whether we have any text at all.
    
    if not (raw_premises or raw_conclusion):
            return 'None', 'no argument'
    
    # Clean up the input and put premises in list format.
    
    premises, conclusion = clean_input(raw_premises, raw_conclusion)
    
    # Check again, because newlines and spaces could have passed the first test.
    
    if not (premises or conclusion):
        return 'None', 'no argument'
    
    # Is anything invalid? (Premise errors take precedence over conclusion.)
    
    if premises:
        i = 0
        while i < len(premises):
            
            valid, error = is_valid(premises[i])
            
            if not valid:
                return 'Error', '{} in premise {}'.format(
                    ERROR_TO_MESSAGE[error], i + 1)
            
            i += 1
        
    if conclusion:
        valid, error = is_valid(conclusion)
        if not valid:
            return 'Error', '{} in conclusion'.format(ERROR_TO_MESSAGE[error])
        
    # Okay, so it's all valid. Do we have a conclusion?
    
    if not conclusion:
        return 'None', 'no conclusion'
        
    # So we have an argument. Translate it.
    
    premises, conclusion, names = translate_all(premises, conclusion)
    
    # Is it circular?
    
    if is_circular(premises, conclusion):
        return 'Valid', 'circular'
    
    # Evaluate the argument.
    
    valid, world, premises_ever_true, conclusion_ever_true,\
        conclusion_always_true = evaluate_argument(premises, conclusion, names)
    
    # Is it valid?
    
    if valid:
        if conclusion_always_true:
            return 'Valid', 'tautology'
        elif not premises_ever_true:
            return 'Valid', 'self-contradictory premises'
        else:
            return 'Valid', ''
    
    # Guess there's only one option left...
    
    if not conclusion_ever_true:
        return 'Invalid', 'contradiction'
        
    info = 'counterexample:\n\n'
    
    # Sort the names in the world.
    
    names = list(world.keys())
    names.sort()
    
    # List the value of each name.
    
    for name in names:
        info += '{}: {}\n'.format(name, world[name])
        
    # Truncate the last newline and return.
    
    info = info[:-1]
    
    return 'Invalid', info