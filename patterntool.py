#!/usr/bin/python
#written for compatability with Python 2.6.1
#Alice Storey, Hunter College
#usage: ./patterntool.py filename

import sys, re

token = "[0-9a-zA-Z'\,\.\?\$]+"
argument = "[a-zA-Z0-9_\-\.,~]+"


		
class Node:
	def __init__(self, value='', term=''):
		self.children = []
		self.value = value
		self.term = term
		self.parent = None
	
	def is_terminal(self):
		return self.term != ''
		
	def is_empty(self):
		return not self.value
		
	def __repr__(self):
		return '%s %s'%(self.value, self.term)
		
	def __eq__(self, other):
		return self.value == other.value
		
	def __ne__(self, other):
		return not self==other

#stores data for a single entry generated from S1
class Pattern:
	def __init__(self):
		self.raw = ''
		self.top = Node()
	
	#Generator support will be added later in the form of tree.
	#For now only extracts terminals and stores the whole entry as a raw string.
	def parse(self, string):
		self.raw = string
		parsed = re.findall( '%s|[\(\)]'%(token), string )
		stack = []
		t = self.top
		
		
		while len(parsed) > 0:
			if parsed[0]=='(':
				if parsed[1] == '(':
					stack.append('0')
					del parsed[0]
				else:
					stack.append(parsed[1])
					del parsed[0:2]
				if t.is_empty(): t.value = stack[-1]
				else: 
					t.children.append(Node(stack[-1]) )
					t.children[-1].parent = t
					t = t.children[-1]
			elif parsed[0] == ')':
				del stack[-1]
				t = t.parent
				del parsed[0]
				if len(stack)==0: parsed = []
			else:
				t.term = parsed[0]
				del parsed[0]
		#raw_input()
		'''
		self.raw = string
		
		tag = '\(S[0-9]+[a-zA-Z]*'
		#generator = '\(' + token + '\s+\('
		terminal = '\(' + token + '\s+' + token + '\)'
		self.tag = re.findall(tag, string)[0]
		for term in re.findall(terminal, string):
			terminal = Terminal()
			(terminal.type, terminal.terminal) = re.findall(token, term)
			self.terminals.append(terminal)
		'''
		
	def tag(self):
		return self.top.value
		
	def write(self, file):
		self.topleftright(self.top, file)
		file.write('\n')
		
	def display(self):
		self.topleftright(self.top, sys.stdout)
		sys.stdout.write('\n')
		
	def topleftright(self, node, output):
		output.write( '(%s'%(node) )
		for child in node.children:
			self.topleftright(child, output)
		output.write(')')
		
	def find(self, key):
		if re.search('\(%s[\s\(\)]'%(key), self.raw): return True
		else: return False
		
	def remove(self, key):
		self.remove_(key, self.top)
		
	def remove_(self, key, node):
		node.children[:] = [child for child in node.children if not child.value==key]
		for child in node.children:
			self.remove_(key, child)
		
	def terminals(self):
		terms = []
		self.terminals_(self.top, terms)
		return terms
	
	def terminals_(self, node, terms):
		if node.is_terminal(): 
			terms.append(node.value)
		else: 
			for child in node.children: 
				self.terminals_(child, terms)
		
	def __eq__(self, other):
		aterms = self.terminals()
		bterms = other.terminals()
		if len(aterms) == len(bterms):
			for i, term in enumerate(aterms):
				if term != bterms[i]: return False
		return True
		
	
#read and parse file
file = open(sys.argv[1])
patterns = []
sentence = ''
for line in file:
	line = line[:-1]
	blankline = '^$'
	beginsentence = '^\s*\(S[a-zA-Z0-9]+'
	if not re.match(blankline, line):
		if re.match(beginsentence, line):
			if not sentence: 
				sentence = line
			else:
				patterns.append(Pattern())
				patterns[-1].parse(sentence)
				sentence = line
		else: sentence += line
patterns.append(Pattern())
patterns[-1].parse(sentence)
file.close()


help = 'q, quit: exit application\n?, help: show this guide\nfind <token>: narrow dataset to patterns with <token>\ndel <token>: remove <token> subtrees from all entries\nunique: remove redudant patterns\nwrite <file>: write current dataset to <file>\nwriteterminals <file>: write just terminals to <file>\norder <id>: change S1 tag to S<id><line#>\n'
argserror = 'Insufficient arguments.\n'


#command loop
quit = False
print help
while not quit:
	cmd = raw_input(">")
	if re.match('quit|^q\s*', cmd, re.I): quit = True
	elif re.match('help|\?', cmd, re.I): print help
	elif re.match('^find$|find\s', cmd, re.I):
		args = re.findall(argument, cmd)
		if len( args ) >= 2:
			patterns[:] = [p for p in patterns if p.find(args[1]) ]
		else: print argserror
	elif re.match('write$|write\s', cmd, re.I):
		args = re.findall(argument, cmd)
		if len( args ) >= 2:
			file = open(args[1], 'w')
			for pattern in patterns: pattern.write(file)
			file.close()
			print "%d lines successfully written."%(len(patterns))
		else: print argserror
	elif re.match('remove$|remove\s', cmd, re.I):
		args = re.findall(argument, cmd)
		if len(args) >= 2:
			for pattern in patterns:
				pattern.remove(args[1])
		else: print argserror
	elif re.match('writeterminals$|writeterminals\s', cmd, re.I):
		args = re.findall(argument, cmd)
		if len( args ) >= 2:
			file = open(args[1], 'w')
			for pattern in patterns:
				file.write(pattern.tag() + ' ')
				for t in pattern.terminals():
					file.write(t + ' ')
				file.write('\n')
			file.close()
			print "%d lines successfully written."%(len(patterns))
		else: print argserror
	elif re.match('unique$|unique\s', cmd, re.I):
		uniques = []
		for p in patterns:
			if p not in uniques:
				uniques.append(p)
		print "%d unique patterns (%d removed)."%(len(uniques), len(patterns) - len(uniques) )
		patterns = uniques
	elif re.match('order$|order\s', cmd, re.I):
		args = re.findall(argument, cmd)
		if len( args ) >= 2:
			for i, pattern in enumerate (patterns):
				pattern.top.value = 'S%s%d'%(args[1], i)
		else: print argserror
		