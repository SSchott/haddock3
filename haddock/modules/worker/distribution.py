import os


class JobCreator:

	def __init__(self):
		self.job_dic = {}
		self.wd = os.getcwd()

		if not os.path.isdir(f'{self.wd}/jobs'):
			os.system(f'mkdir {self.wd}/jobs')

		if not os.path.isdir(f'{self.wd}/out'):
			os.system(f'mkdir {self.wd}/out')

	def delegate(self, recipe_str, input_model_list):
		""" Give one recipe to each Model """

		# FIXME: Need to identify what will be the name of the final structure.

		# recipe_str = input_script.recipe
		for i, model in enumerate(input_model_list):
			model_name = model.split('/')[-1].split('.')[0]

			input_f = f'{self.wd}/jobs/{model_name}.inp'
			output_f = f'{self.wd}/out/{model_name}.out'

			tbw = '! Input structure\n'
			tbw += f'eval ($file="{model}")\n' + recipe_str
			with open(input_f, 'w') as f:
				f.write(tbw)
			f.close()

			self.job_dic[i] = (input_f, output_f)

		return self.job_dic
