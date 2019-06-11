// JavaScript Document

// CONSTANTS

var AND = ['^', '&', '+', ]
var OR = ['v', '/', ]
var IF = ['>', ]
var IFF = ['=', ]
var NOT = ['~', '-', '!']
var LEFT = ['(', ]
var RIGHT = [')', ]
var SPACE = [' ', ]

var ALL_SYMBOLS = AND.concat(OR, IF, IFF, NOT, LEFT, RIGHT, SPACE)
var ALL_NAMES = ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

// Because JS can't use arrays as property names, we need to associate these strings to both the array to check and the result...
var SYMBOL_TO_JS = {
    'AND': [AND, ' && '],
    'OR': [OR, ' || '],
    'IF': [IF, ' === false || '],
    'IFF': [IFF, ' === '],
    'NOT': [NOT, ' ! '],
    'LEFT': [LEFT, ' ( '],
    'RIGHT': [RIGHT, ' ) '],
    'SPACE': [SPACE, ' ']
}

// During validity checking, this dictionary converts a code to a message.
var ERROR_TO_MESSAGE = {
    1: 'invalid character',
    2: 'improper brackets',
    3: 'faulty syntax'
}

// IE8 and earlier does not have the Array methods indexOf or filter
if (!Array.indexOf) {
    Array.prototype.indexOf = function (obj) {
        for (var i = 0; i < this.length; i += 1) {
            if (this[i] == obj) {
                return i
            }
        }

        return -1;

    }
}

if (!('filter' in Array.prototype)) {
    Array.prototype.filter = function (filter, that /*opt*/ ) {
        var other = [],
            v
        for (var i = 0, n = this.length; i < n; i += 1) {
            if (i in this && filter.call(that, v = this[i], i, this)) {
                other.push(v)
            }
        }

        return other
    }
}

// String does not have a count method
String.prototype.count = function (sub, allow_overlap) {

    sub += ''
    if (sub.length <= 0) {
        return string.length + 1
    }

    var count = 0
    var i = 0
    var step = sub.length
    if (allow_overlap) {
        step = 1
    }

    while (true) {
        i = this.indexOf(sub, i)
        if (i >= 0) {
            count += 1
            i += step
        } else {
            break
        }
    }

    return count
}

// WORLD GENERATION

function get_worlds(names) {
    var worlds = []
    var rows = Math.pow(2, names.length)
    for (var i = 0; i < rows; i += 1) {
        worlds.push({})
    }

    for (var pos = 0; pos < names.length; pos += 1) {
        var name = names[pos]
        var alternate = rows / (Math.pow(2, pos + 1))

        var row_outer = 0
        var row_inner = row_outer
        var value = true

        while (row_outer < rows) {
            row_inner = row_outer

            while (row_inner < row_outer + alternate) {
                worlds[row_inner][name] = value
                row_inner += 1
            }

            row_outer = row_inner
            value = !value
        }
    }

    return worlds
}

function get_dummy_world(names) {
    var world = {}

    for (var i = 0; i < names.length; i += 1) {
        world[names[i]] = true
    }

    return world
}

// LOGIC EVALUATION

function evaluate_world(premises, conclusion, world) {
    var valid = true
    var premises_true = false
	var conclusion_true = eval(conclusion)
	
	if (premises == false) {
		premises_true = true
		valid = conclusion_true
	} else {

        var unified_premises = ''
        for (var i = 0; i < premises.length; i += 1) {
            unified_premises += '(' + premises[i] + ') && '
        }

        unified_premises = unified_premises.slice(0, -4)

        if (eval(unified_premises)) {
            valid = conclusion_true
            premises_true = true
        }
	}

    return [valid, premises_true, conclusion_true]
}

function evaluate_argument(premises, conclusion, names) {
	
	var always_valid = true
    var premises_ever_true = false
	var conclusion_ever_true = false
	var conclusion_always_true = true
	var counterexample = {}
	
    var worlds = get_worlds(names)

    for (var i = 0; i < worlds.length; i += 1) {
        var result = evaluate_world(premises, conclusion, worlds[i])
        var valid = result[0]
        var premises_true = result[1]
		var conclusion_true = result[2]
		if (!valid) {
			counterexample = worlds[i]
		}
		
		always_valid = Math.min(always_valid, valid)
        premises_ever_true = Math.max(premises_ever_true, premises_true)
		conclusion_ever_true = Math.max(conclusion_ever_true, conclusion_true)
		conclusion_always_true = Math.min(conclusion_always_true, conclusion_true)
    }

    return [always_valid, counterexample, premises_ever_true, conclusion_ever_true, conclusion_always_true]
}

// INPUT CLEANUP AND TRANSLATION

function translate(string) {
    var translation = ''
    var names = []

    for (var i = 0; i < string.length; i += 1) {
        var char = string[i]

        if (ALL_SYMBOLS.indexOf(char) != -1) {
            for (symbol in SYMBOL_TO_JS) {
                array = SYMBOL_TO_JS[symbol][0]
                equivalent = SYMBOL_TO_JS[symbol][1]
                if (array.indexOf(char) != -1) {
                    translation += equivalent
                    break
                }
            }
        } else if (ALL_NAMES.indexOf(char) != -1) {
            names.push(char)
            translation += ' world["' + char + '"] '
        }
    }

    while (translation.indexOf('  ') != -1) {
        translation = translation.replace('  ', ' ')
    }

    translation = translation.trim()

    return [translation, names]
}

function translate_all(premises, conclusion) {
    var all_names = []
    var translated_premises = []

    for (var i = 0; i < premises.length; i += 1) {
        var result = translate(premises[i])
        var translation = result[0]
        var names = result[1]
        translated_premises.push(translation)
        all_names.push.apply(all_names, names)
    }

    var result = translate(conclusion)
    var translation = result[0]
    var names = result[1]
    var translated_conclusion = translation
    all_names.push.apply(all_names, names)

    all_names = all_names.filter(function (elem, pos) {
        return all_names.indexOf(elem) == pos
    })

    return [translated_premises, translated_conclusion, all_names]
}

function clean_input(premises, conclusion) {
    premises = premises.split('\n')
    var premises_clean = []

    for (var i = 0; i < premises.length; i += 1) {
        premise = premises[i].trim()
        if (premise) {
            premises_clean.push(premise)
        }
    }
	
	var conclusion_clean = conclusion.trim()

    return [premises_clean, conclusion_clean]
}

// VALIDITY AND CIRCULARITY CHECKING

function get_bracket_subsegment(string) {
    var sub = ''
    var depth = 1

    for (var i = 0; i < string.length; i += 1) {
        depth += string[i] == '('

        if (depth == 1) {
            sub += string[i]
        }

        depth -= string[i] == ')'

        if (depth == 0) {
            break
        }
    }

    return sub.slice(0, -1)
}

function good_brackets(string) {
    if (string.count('(') != string.count(')')) {
        return false
    }

    for (var i = 0; i < string.length; i += 1) {
        string = string.slice(i)
        var bracket_start = string.indexOf('(')

        if (bracket_start == -1) {
            break
        }

        var bracket_sub = get_bracket_subsegment(string.slice(bracket_start + 1))

        if (!bracket_sub.trim()) {
            return false
        }
    }

    return true
}

function is_valid(string) {
	
	// First test
    for (var i = 0; i < string.length; i += 1) {
        char = string[i]
        if (ALL_NAMES.indexOf(char) + ALL_SYMBOLS.indexOf(char) == -2) {
            return [false, 1]
        }
    }

    // Second test
    if (!good_brackets(string)) {
        return [false, 2]
    }

    // Third test
    var result = translate(string)
    var translation = result[0]
    var names = result[1]
    var world = get_dummy_world(names)

    try {
        !!eval(translation)
        return [true, null]
    } catch (err) {
        return [false, 3]
    }
}

function is_circular(premises, conclusion) {
	if (premises == false) {
		return false
	}
	
    while (conclusion[0] == '(' && conclusion[conclusion.length - 1] == ')') {
        conclusion = conclusion.slice(1, -1)
        conclusion = conclusion.trim()
    }

    var enough = premises.sort(function (a, b) {
        return b.length - a.length;
    })[0].length

    while (conclusion.length <= enough) {
        if (premises.indexOf(conclusion) != -1) {
            return true
        }

        conclusion = '( ' + conclusion + ' )'
    }

    return false
}

// INTERFACE

function get_result_text(raw_premises, raw_conclusion) {
	// Short-circuit: check whether we have any text at all.
    if (!(raw_premises || raw_conclusion)) {
        return ['None', 'no argument']
    }
	
    // Clean up input and put premises in list format
    var result = clean_input(raw_premises, raw_conclusion)
    var premises = result[0]
    var conclusion = result[1]
	
    // Check again, because newlines and spaces would have passed the first test.
    if (premises == false && !conclusion) { // "!array" only checks if the array exists
        return ['None', 'no argument']
    }

    // Is anything invalid? (Premise errors take precedence over conclusion)
	if (premises != false) { // Short-circuit
		
        var i = 0
        while (i < premises.length) {
            var result = is_valid(premises[i])
            var valid = result[0]
            var error = result[1]
            if (!valid) {
                return ['Error', ERROR_TO_MESSAGE[error] + '\nin premise ' + (i + 1)]
            }

        i += 1
        }
	}

    if (conclusion) { // Short-circuit
        var result = is_valid(conclusion)
        var valid = result[0]
        var error = result[1]
        if (!valid) {
            return ['Error', ERROR_TO_MESSAGE[error] + '\nin conclusion']
        }
    }
	
	// Okay, so it's all valid. Do we have both a conclusion?
    if (!conclusion) {
        return ['None', 'no conclusion']
    }

    // So we have an argument. Translate it.
    var result = translate_all(premises, conclusion)
    premises = result[0]
    conclusion = result[1]
    var names = result[2]

    // Is it circular?
    if (is_circular(premises, conclusion)) {
        return ['Valid', 'circular']
    }

    // Evalaute the argument.
    result = evaluate_argument(premises, conclusion, names)
    var valid = result[0]
    var world = result[1]
    var premises_ever_true = result[2]
	var conclusion_ever_true = result[3]
	var conclusion_always_true = result[4]

    // Is it valid?
    if (valid) {
		if (conclusion_always_true) {
			return ['Valid', 'tautology']
		} else if (!premises_ever_true) {
            return ['Valid', 'self-contradictory premises']
        } else {
            return ['Valid', '']
        }
    }

    // Guess there's only one option left...
	if (!conclusion_ever_true) {
		return ['Invalid', 'contradiction']
	}
	
    var info = 'counterexample:\n\n'

    // Sort the names in the world.
    var names = []
    for (name in world) {
        names.push(name)
    }
    names.sort()

    // List the value of each name.

    for (var i = 0; i < names.length; i += 1) {
        name = names[i]
        info += name + ': ' + world[name] + '\n'
    }

    info = info.slice(0, -1)

    return ['Invalid', info]
}