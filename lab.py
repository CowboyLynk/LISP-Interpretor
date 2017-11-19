"""6.009 Lab 8A: carlae Interpreter"""

import sys


class EvaluationError(Exception):
	"""Exception to be raised if there is an error during evaluation."""
	pass


# ==============================
# MARK: All the code for parsing
# ==============================
def tokenize(source):
	"""
	Splits an input string into meaningful tokens (left parens, right parens,
	other whitespace-separated values).  Returns a list of strings.

	Arguments:
		source (str): a string containing the source code of a carlae
					  expression
	"""
	# splits the source up into lines
	lines = source.split("\n")

	tokens = []
	specials = {"(", ")", " "}

	# tokens the lines
	for line in lines:
		# builds up a current token until we reach a special char ("(", ")", ";", " ")
		token = ""
		for char in line:
			# if we reach a comment, go on the the next line
			if char == ";":
				break

			if char in specials:
				# Reached end of token, if there's something to add, add it to the tokens
				if token:
					tokens.append(token)
					token = ""

				# Add it to tokens if it's a paren.
				if char != " ":
					tokens.append(char)
					token = ""
			else:
				token += char

		# makes sure to pick up the last token
		if token:
			tokens.append(token)
	return tokens


def find_matching_paren(L):
	"""
	This is a helper function
	:param L: A list of tokens with the start being the first parenthesis
	:return: the index of the matching parenthesis
	"""
	paren_counter = 0
	for i in range(len(L)):
		token = L[i]
		if token == "(":
			paren_counter += 1
		elif token == ")":
			paren_counter -= 1

		# found the matching parenthesis
		if paren_counter == 0 and token == ")":
			return i

	# there was no matching parenthesis
	return None


def parse(tokens):
	"""
	Parses a list of tokens, constructing a representation where:
		* symbols are represented as Python strings
		* numbers are represented as Python ints or floats
		* S-expressions are represented as Python lists

	Arguments:
		tokens (list): a list of strings representing tokens
	"""
	def rec_parse(tokens):
		"""
		:param tokens: a list of strings representing tokens with VALID PARENTHESIS
		:return: returns the thing
		"""
		# BASE CASE: We've passed in a list of only one thing so return that thing
		if len(tokens) == 1:
			token = tokens[0]
			# try casting it to an int
			try:
				token = int(token)
			except ValueError:
				# try casting it to a float
				try:
					token = float(token)
				# leave it as is
				except ValueError:
					pass
			return token

		# Checks if we're just evaluating for one full parenthetical
		if tokens[0] == "(" and find_matching_paren(tokens) == len(tokens) - 1:
			# just ignore the parenthesis
			tokens = tokens[1:-1]

		# else: start going through each element in tokens
		result = []
		i = 0
		while i < len(tokens):
			token = tokens[i]
			# We've found the start of a parenthetical
			if token == "(":
				# finds the end of the parenthetical and makes recursive call
				paren_counter = 0
				for j in range(i, len(tokens)):
					if tokens[j] == "(":
						paren_counter += 1
					elif tokens[j] == ")":
						paren_counter -= 1

					# found the closing parenthesis
					if paren_counter == 0 and tokens[j] == ")":
						# make the recursive call and break
						result.append(rec_parse(tokens[i:j+1]))
						# jumps to next token after the paren'
						i = j
						break

			# It's not an element in closed in parenthesis
			# We don't have to worry about ) because we've already checked for valid parenthesis
			else:
				result.append(rec_parse([token]))
			i += 1

		return result

	# Check for valid parenthesis
	paren_counter = 0
	for token in tokens:
		if token == "(":
			paren_counter += 1
		elif token == ")":
			paren_counter -= 1
		if paren_counter < 0:
			raise SyntaxError
	if paren_counter != 0:
		raise SyntaxError

	# Call rec_parse
	return rec_parse(tokens)


# =======================
# MARK: builtin functions
# =======================
class Builtins:

	@staticmethod
	def mul(args: list):
		result = args[0]
		for arg in args[1:]:
			result *= arg
		return result

	@staticmethod
	def div(args: list):
		result = args[0]
		for arg in args[1:]:
			result /= arg
		return result

	@staticmethod
	def eq(args: list):
		for i, arg in enumerate(args):
			for j in range(i+1, len(args)):
				arg2 = args[j]
				if arg != arg2:
					return False
		return True


	@staticmethod
	def gt(args: list):
		for i in range(len(args) - 1):
			arg1 = args[i]
			arg2 = args[i+1]
			if arg1 <= arg2:
				return False
		return True

	@staticmethod
	def gt_eq(args: list):
		for i in range(len(args) - 1):
			arg1 = args[i]
			arg2 = args[i+1]
			if arg1 < arg2:
				return False
		return True

	@staticmethod
	def lt(args: list):
		for i in range(len(args) - 1):
			arg1 = args[i]
			arg2 = args[i+1]
			if arg1 >= arg2:
				return False
		return True

	@staticmethod
	def lt_eq(args: list):
		for i in range(len(args) - 1):
			arg1 = args[i]
			arg2 = args[i+1]
			if arg1 > arg2:
				return False
		return True

	@staticmethod
	def opposite(args: list):
		return not args[0]

	@staticmethod
	def list(args: list):
		if args:  # if there is at least one argument
			start = LinkedList(args[0])
			current = start
			for arg in args[1:]:
				new_ll = current.add_next(arg)
				current = new_ll
			return start
		else:
			return None

	@staticmethod
	def car(args):
		L = args[0]
		if L:
			return L.get_elt()
		else:
			raise EvaluationError

	@staticmethod
	def cdr(args):
		L = args[0]
		if L:
			return L.get_next()
		else:
			raise EvaluationError

	@staticmethod
	def length(args):
		L = args[0]
		if L is None:
			return 0
		else:
			return Builtins.length([L.get_next()]) + 1

	@staticmethod
	def elt_at_index(args):
		L = args[0]
		if not L:
			raise EvaluationError
		index = args[1]
		if index == 0:
			return L.get_elt()
		else:
			return Builtins.elt_at_index([L.get_next(), index - 1])

	@staticmethod
	def concat(args):
		concat = None
		for i in range(0, len(args)):
			if args[i] is None:
				continue
			LL = args[i].make_copy()
			if concat is None:  # starts the beginning of the linked list
				concat = LL
			else:
				concat.get_last().set_next(LL)
		return concat

	@staticmethod
	def map(args):
		func = args[0]
		new_LL = args[1].make_copy()
		for list_item in new_LL:  # iterates through each of the LL items
			list_item.set_elt(func([list_item.get_elt()]))
		return new_LL

	@staticmethod
	def filter(args):
		func = args[0]
		new_LL = None
		for list_item in args[1]:  # iterates through each of the LL items
			elt = list_item.get_elt()
			if func([elt]):
				new = LinkedList(elt)
				if new_LL is None:
					new_LL = new
				else:
					new_LL.get_last().set_next(new)
		return new_LL

	@staticmethod
	def reduce(args):
		func = args[0]
		new_LL = args[1].make_copy()
		result = args[2]
		for list_item in new_LL:  # iterates through each of the LL items
			elt = list_item.get_elt()
			result = func([result, elt])
		return result

	@staticmethod
	def begin(args):
		return args[-1]

carlae_builtins = {
	'+': sum,
	'-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
	'*': Builtins.mul,
	"/": Builtins.div,
	"=?": Builtins.eq,
	">": Builtins.gt,
	">=": Builtins.gt_eq,
	"<": Builtins.lt,
	"<=": Builtins.lt_eq,
	"not": Builtins.opposite,
	"list": Builtins.list,
	"car": Builtins.car,
	"cdr": Builtins.cdr,
	"length": Builtins.length,
	"elt-at-index": Builtins.elt_at_index,
	"concat": Builtins.concat,
	"map": Builtins.map,
	"filter": Builtins.filter,
	"reduce": Builtins.reduce,
	"begin": Builtins.begin,
	"#t": True,
	"#f": False
}


# ============================================
# MARK: contains all the builtin objects types
# ============================================
class Env:

	def __init__(self, parent=carlae_builtins):
		self.parent = parent
		self.symbols = {}  # is a dictionary mapping the variable name to its value

	def define_symbol(self, sym, value):
		self.symbols[sym] = value

	def set_bang(self, sym, value):
		if sym in self:
			self.symbols[sym] = value
		else:
			try:
				self.parent.set_bang(sym, value)
			except:
				raise EvaluationError

	def __contains__(self, item):
		return item in self.symbols

	def __getitem__(self, item):
		# Tries to find the item in itself
		if item in self:
			return self.symbols[item]
		# Looks for it in the parent env
		else:
			try:
				return self.parent[item]
			# couldn't find it in the parent so raise an error
			except KeyError:
				raise EvaluationError

	def __repr__(self):
		return str(self.symbols)


class Lambda:

	def __init__(self, params, express, env):
		self.env = env
		self.params = params
		self.expression = express

	def __call__(self, *args):
		if len(args[0]) != len(self.params):
			raise EvaluationError

		new_env = Env(self.env)  # creates a new environment

		# binds the function's parameters to the values that are passed to it
		for i, param in enumerate(self.params):
			try:  # sees the if the value can be simplified
				new_env.define_symbol(param, evaluate(args[0][i], self.env))
			except EvaluationError:
				new_env.define_symbol(param, args[0][i])

		return evaluate(self.expression, new_env)

	def __repr__(self):
		return "LambdaObject: " + str(self.params)


class LinkedList:

	def __init__(self, elt, next=None):
		self.elt = elt  # is the element at this position in the list
		self.next = next  # points to an instance of LinkedList that is the next element in the list

	def get_elt(self):
		return self.elt

	def set_elt(self, elt):
		self.elt = elt

	def get_next(self):
		return self.next

	def set_next(self, LL):
		self.next = LL

	def add_next(self, n_elt):
		next_ll = LinkedList(n_elt)
		self.next = next_ll
		return next_ll

	def get_last(self):
		if self.next is None:
			return self
		else:
			return self.next.get_last()

	def make_copy(self):
		if self.next is not None:
			return LinkedList(self.elt, self.next.make_copy())
		else:
			return LinkedList(self.elt, None)

	def __repr__(self):
		result = "LinkedList: [ "
		for LL in self:
			result += str(LL.get_elt()) + " "
		result += "]"
		return result

	def __iter__(self):
		current = self
		yield current
		while current.get_next() is not None:
			yield current.get_next()
			current = current.get_next()


# ===============================================================
# MARK: all the the evaluation code for interpreting the language
# ===============================================================
def evaluate_file(file_name, env=None):
	if not env:
		env = Env()
	file = open(file_name).read()
	print(file)
	tokens = tokenize(file)
	expression = parse(tokens)
	return evaluate(expression, env)


def result_and_env(tree, env=None):
	if not env:
		env = Env()
	out = evaluate(tree, env)
	return out, env


def evaluate(tree, env=None):
	"""
	Evaluate the given syntax tree according to the rules of the carlae
	language.

	Arguments:
		tree (type varies): a fully parsed expression, as the output from the
							parse function
	"""
	# Fixes the default case
	if not env:
		env = Env()
	if tree == []:
		raise EvaluationError

	# BASE CASES
	if not isinstance(tree, list):
		if isinstance(tree, (int, float)):  # if its a number, return that number
			return tree
		else:  # tries to find that symbol
			# Raises EvaluationError if it can't find it
			return env[tree]

	# Check for the "define" keyword: assigns a value to a variable
	if tree[0] == "define":
		# here's the shortcut for defining a function
		if isinstance(tree[1], list):
			val = Lambda(tree[1][1:], tree[2], env)
			env.define_symbol(tree[1][0], val)  # sets the value of tree[1]
			return val
		else:
			val = evaluate(tree[2], env)
			env.define_symbol(tree[1], val)  # sets the value of tree[1]
			return val
	# checks for the "lambda" keyword: makes a user defined function
	elif tree[0] == "lambda":
		return Lambda(tree[1], tree[2], env)
	# checks for the "if" keyword
	elif tree[0] == "if":
		result = evaluate(tree[1], env)
		if result:
			return evaluate(tree[2], env)
		else:
			return evaluate(tree[3], env)
	elif tree[0] == "and":
		for arg in tree[1:]:
			if not evaluate(arg, env):
				return False
		return True
	elif tree[0] == "or":
		for arg in tree[1:]:
			if evaluate(arg, env):
				return True
		return False
	elif tree[0] == "let":
		new_env = Env(env)
		for assignment in tree[1]:  # sets all the temporary assignments for the let
			new_env.define_symbol(assignment[0], evaluate(assignment[1], env))
		return evaluate(tree[2], new_env)
	elif tree[0] == "set!":
		val = evaluate(tree[2], env)
		env.set_bang(tree[1], val)
		return val
	# checks the case where if the first element is a function
	elif isinstance(tree[0], list):
		try:
			new_lambda = evaluate(tree[0], env)
			return new_lambda(tree[1:])
		# checks that it's not a list whose first element is not a function
		except:
			raise EvaluationError
	# Evaluates any functions
	else:
		args = []
		for i in range(1, len(tree)):
			args.append(evaluate(tree[i], env))
		return env[tree[0]](args)


if __name__ == '__main__':
	# code in this block will only be executed if lab.py is the main file being
	# run (not when this module is imported)

	# REPL Code
	repl_env = Env()
	# runs the pre-defined functions in the text files first
	for file_name in sys.argv[1:]:
		evaluate_file(file_name, repl_env)
	while True:
		user_in = input("in> ")
		if user_in == "QUIT":
			break
		try:
			tokens = tokenize(user_in)
			expression = parse(tokens)
			print("  out>", evaluate(expression, repl_env))
		except:
			print("  out> Error")
		print()
