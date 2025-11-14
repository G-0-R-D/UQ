
def build(ENV):

	class SnapInternalCompilerPreprocess(object):

		# c does not allow definitions inside of other functions, nor imports, so to
		# get around that we make sure to create all definitions in the module first,
		# and then just initialize them into the ENV in <MODULENAME>_MAINBODY(ENV) ->
		# which represents the import / run of the module
	
################ ROOT NODES:

		def preprocess_module(self, ROOT, N): pass

		def preprocess_input_expression(self, ROOT, N): pass
		def preprocess_interactive(self, ROOT, N): pass
		def preprocess_function_type(self, ROOT, N): pass

################ LITERALS:

		def preprocess_constant(self, ROOT, N): pass

		def preprocess_formatted_value(self, ROOT, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))
		def preprocess_joined_string(self, ROOT, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))

		def preprocess_list(self, ROOT, N): pass
		def preprocess_tuple(self, ROOT, N): pass
		def preprocess_set(self, ROOT, N): pass
		def preprocess_dictionary(self, ROOT, N): pass

################ VARIABLES:

		def preprocess_name(self, ROOT, N): pass
		# TODO phase these out of generalized ast?  load/store context is bypassed entirely by using _attr()/_item() placeholder instead....
		def preprocess_load(self, ROOT, N): pass
		def preprocess_store(self, ROOT, N): pass
		def preprocess_remove(self, ROOT, N): pass

		def preprocess_starred(self, ROOT, N): pass

################ EXPRESSIONS:

		def preprocess_expression(self, ROOT, N): pass
		def preprocess_unary_operation(self, ROOT, N): pass

		def preprocess_unary_add(self, ROOT, N): pass
		def preprocess_unary_subtract(self, ROOT, N): pass
		def preprocess_not(self, ROOT, N): pass
		def preprocess_bitwise_invert(self, ROOT, N): pass

		def preprocess_binary_operation(self, ROOT, N): pass

		def preprocess_add(self, ROOT, N): pass
		def preprocess_subtract(self, ROOT, N): pass
		def preprocess_multiply(self, ROOT, N): pass
		def preprocess_divide(self, ROOT, N): pass
		def preprocess_floor_divide(self, ROOT, N): pass
		def preprocess_modulo(self, ROOT, N): pass
		def preprocess_power(self, ROOT, N): pass
		def preprocess_bitwise_left_shift(self, ROOT, N): pass
		def preprocess_bitwise_right_shift(self, ROOT, N): pass
		def preprocess_bitwise_or(self, ROOT, N): pass
		def preprocess_bitwise_xor(self, ROOT, N): pass
		def preprocess_bitwise_and(self, ROOT, N): pass
		def preprocess_matrix_multiply(self, ROOT, N):
			# not even sure what this is for?  implement a __mul__ on a matrix instead maybe?  anyways, doesn't apply here.
			raise NotImplementedError(repr(N['__type__']))

		def preprocess_bool_operation(self, ROOT, N):
			if len(N['values']) > 2:
				# nested operations need to be encompassed in own function...
				pre = self.add_predefinition(N)
				pre['predefined_name'] = self.module_name + '_bool_op' + str(pre['index'])

		def preprocess_and(self, ROOT, N): pass
		def preprocess_or(self, ROOT, N): pass


		def preprocess_comparison(self, ROOT, N):
			if len(N['operators']) > 1:
				pre = self.add_predefinition(N)
				pre['predefined_name'] = self.module_name + '_compare' + str(pre['index'])

		def preprocess_equal(self, ROOT, N): pass
		def preprocess_not_equal(self, ROOT, N): pass
		def preprocess_less_than(self, ROOT, N): pass
		def preprocess_less_or_equal(self, ROOT, N): pass
		def preprocess_greater_than(self, ROOT, N): pass
		def preprocess_greater_or_equal(self, ROOT, N): pass
		def preprocess_is(self, ROOT, N): pass
		def preprocess_is_not(self, ROOT, N): pass
		def preprocess_in(self, ROOT, N): pass
		def preprocess_not_in(self, ROOT, N): pass

		def preprocess_call(self, ROOT, N): pass

		def preprocess_keyword(self, ROOT, N): pass
		def preprocess_if_expression(self, ROOT, N): pass
		def preprocess_attribute(self, ROOT, N): pass

		def preprocess_named_expression(self, ROOT, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))

################ SUBSCRIPTING:

		def preprocess_subscript(self, ROOT, N): pass
		def preprocess_slice(self, ROOT, N): pass


################ COMPREHENSIONS: # TODO these will need to generate custom functions to define them

		def preprocess_list_comprehension(self, ROOT, N):
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_list_comp' + str(pre['index'])
		def preprocess_set_comprehension(self, ROOT, N):
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_set_comp' + str(pre['index'])
		def preprocess_generator_comprehension(self, ROOT, N):
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_gen_comp' + str(pre['index'])
		def preprocess_dictionary_comprehension(self, ROOT, N):
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_dict_comp' + str(pre['index'])
		def preprocess_comprehension(self, ROOT, N):
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_comp' + str(pre['index'])

################ STATEMENTS:

		def preprocess_assign(self, ROOT, N): pass
		def preprocess_annotated_assign(self, ROOT, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))
		def preprocess_augmented_assign(self, ROOT, N): pass
		def preprocess_raise(self, ROOT, N): pass
		def preprocess_assert(self, ROOT, N): pass
		def preprocess_delete(self, ROOT, N): pass
		def preprocess_pass(self, ROOT, N): pass
		def preprocess_type_alias(self, ROOT, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))

################ IMPORTS: # TODO?

		# backend modules will import using same build mechanism, so aside from 'snap.h' there are no other includes...
		# a main module will create the main function, include all the modules, build them all into the ENV, and then
		# begin execution...

		def preprocess_import(self, ROOT, N): pass
		def preprocess_import_from(self, ROOT, N): pass
		def preprocess_import_alias(self, ROOT, N): pass

################ CONTROL FLOW:

		def preprocess_if(self, ROOT, N): pass
		def preprocess_for(self, ROOT, N): pass
		def preprocess_while(self, ROOT, N): pass
		def preprocess_break(self, ROOT, N): pass
		def preprocess_continue(self, ROOT, N): pass

		def preprocess_try(self, ROOT, N):
			"""
			if there is a finally clause we need to double nest the functions, otherwise we can get away with just one

			error check after the return
			"""
			'' # TODO just define the try body in a function, and then check if ENV exception and if so then attempt to handle it (exception can be in main code section)
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_try' + str(pre['index'])

		def preprocess_try_star(self, ROOT, N): raise NotImplementedError('(v3.8+)', repr(N['__type__']))
		def preprocess_exception(self, ROOT, N): pass
		def preprocess_with(self, ROOT, N):
			# TODO just make a function for the with call, call the __enter__ at the beginning of the call and __exit__ *outside* the function after the call, then check errors
			raise NotImplementedError()
		def preprocess_with_item(self, ROOT, N): pass

################ PATTERN MATCHING: TODO v3.8+

################ TYPE ANNOTATIONS: TODO v3.8+

################ TYPE PARAMETERS: TODO v3.8+

################ FUNCTION AND CLASS DEFINITIONS:

		def preprocess_function_definition(self, ROOT, N):
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_func_' + N['name']

		def preprocess_lambda(self, ROOT, N):
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_lambda' + str(pre['index'])

		def preprocess_arguments(self, ROOT, N): pass
		def preprocess_argument(self, ROOT, N): pass
		def preprocess_return(self, ROOT, N): pass

		def preprocess_yield(self, ROOT, N): raise TypeError(repr(N['__type__']), '(async forbidden in backend)')
		def preprocess_yield_from(self, ROOT, N): raise TypeError(repr(N['__type__']), '(async forbidden in backend)')

		def preprocess_global(self, ROOT, N): pass
		def preprocess_non_local(self, ROOT, N): pass

		def preprocess_class_definition(self, ROOT, N):
			pre = self.add_predefinition(N)
			pre['predefined_name'] = self.module_name + '_class_' + N['name']
			pre['predefined_type_name'] = self.module_name + '_type_' + N['name']

			# TODO predefine methods as well...
			pre['methods'] = []
			for sub in N['body']:
				if sub['__type__'] == 'function_definition':
					pre['methods'].append(N)


		def preprocess_newline(self, ROOT, N): pass


	ENV.SnapInternalCompilerPreprocess = SnapInternalCompilerPreprocess

