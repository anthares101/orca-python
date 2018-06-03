
import os, sys, csv, json, time, datetime, re, collections
import pandas as pd
import numpy as np

from sklearn.grid_search import GridSearchCV
from sklearn.metrics.scorer import make_scorer

import DSU
from Results import Results

class Utilities:
	"""

	"""


	def __init__(self, api_path, general_conf, configurations):

		"""

		"""

		#TODO: Mejorar forma de obtener el path hasta la carpeta base (para que no dependa de la ubicacion del fichero config)
		#		Por ejemplo, del api path, quitando carpetas por la derecha hasta llegar a el nombre de la carpeta .../orca_python/
		self.api_path_ = api_path
		self.general_conf_ = general_conf
		self.configurations_ = configurations


		#TODO: Obtener el numero de salidas para cada dataset sin que se tenga que especificar en el fichero de configuracion
		# ---> En principio no es necesario, pero se puede conseguir tras leer las salidas de los datos, restando al mayor valor
		#		de las salidas el menor valor y se le suma 1.

		print "\n###############################"
		print "\tLoading Start"
		print "###############################"

		self.datasets_ = {}
		# Process each dataset provided by user
		for x in general_conf['datasets'].split(','):

			dataset_name = x.strip()

			#Check if basedir has a final backslash or not
			if general_conf['basedir'][-1] == '/':
				file_path = general_conf['basedir'] + dataset_name + '/'
			else:
				file_path = general_conf['basedir'] + "/" + dataset_name + '/'


			print "Loading dataset", dataset_name, "info..."
			self.datasets_[os.path.basename(os.path.normpath(file_path))] = self._loadDataset(file_path)



	def _loadDataset(self, file_path):

		"""

		"""

		# Looks for all files specified as part of dataset in given folder and orders 'em
		train_files = []
		test_files = []

		for filename in os.listdir(file_path):

			if not os.path.isdir(filename):

				if filename.startswith("train_"):
					train_files.append(file_path + filename)

				elif filename.startswith("test_"):
					test_files.append(file_path + filename)

		train_files.sort(), test_files.sort()


		# Get input and output variables from dataset files
		partition_list = []
		for train_file, test_file in zip(train_files, test_files):


			#Declaring partition DSU
			partition = DSU.DSU(file_path, train_file[ train_file.find('.') + 1 : ])

			# Get inputs and outputs from partition
			partition.train_inputs, partition.train_outputs = self._readFile(train_file)
			partition.test_inputs, partition.test_outputs = self._readFile(test_file)

			# Append DSU to begining of list
			partition_list.append(partition)


		# Save info to dataset
		return partition_list




	def _readFile(self, filename):
		"""

		"""

		f = pd.read_csv(filename, header=None)

		inputs = f.values[:,0:(-1)]
		outputs = f.values[:,(-1)]

		return inputs, outputs



	def runExperiment(self):
		"""

		"""


		print "\n###############################"
		print "\tRunning Experiment"
		print "###############################"


		# Adding algorithm folder to sys path. Needed to import modules from different folders
		sys.path.insert(0, 'Algorithms/')

		self.results_ = Results()	# Creates results object, that will store all different metrics for each algorithm and dataset


		# Iterating over all different datasets
		for dataset_name, dataset in self.datasets_.iteritems():

			print "\nRunning", dataset_name, "dataset..."
			print "--------------------------"

			# Iterating over all different algorithm configurations
			for conf_name, configuration in self.configurations_.iteritems():

				print "Running", configuration["algorithm"], "algorithm"

				# TODO: Comprobar que los algoritmos dados son correctos (y el resto de parametros), sino parar la ejecucion
				#		Hacer que todas las metricas y algoritmos sean upper
				module = __import__(configuration["algorithm"])
				algorithm = getattr(module, configuration["algorithm"].upper())

				# Iterating over all partitions in each dataset
				metrics_list = []
				for partition in dataset:

					if partition.partition != "csv":
						print "  Running Partition", partition.partition

					# Finding optimal parameters
					optimal_estimator = self._getOptimalEstimator(partition, algorithm, configuration["parameters"])


					# Creating tuples with each specified tuple and passing it to specified dataframe
					metrics = collections.OrderedDict()
					for metric_name in self.general_conf_['metrics'].split(','):

						module = __import__("Metrics")
						metric = getattr(module, metric_name.strip().lower())

						train_predicted_y = optimal_estimator.predict(partition.train_inputs)
						train_score = metric(partition.train_outputs, train_predicted_y)

						test_predicted_y = optimal_estimator.predict(partition.test_inputs)
						test_score = metric(partition.test_outputs, test_predicted_y)

						metrics['train_' + metric_name.strip()] = train_score
						metrics['test_' + metric_name.strip()] = test_score

					metrics_list.append(metrics)

				self.results_.addRecord(dataset_name, configuration['algorithm'], metrics_list)



	def _getOptimalEstimator(self, partition, algorithm, parameters):

		"""

		"""
		module = __import__("Metrics")
		metric = getattr(module, self.general_conf_['cv_metric'].lower().strip())

		# TODO: Cuidado con el greater is better (MAE es un indicador que funciona a la inversa - menor es mejor)
		scoring_function = make_scorer(metric, greater_is_better=True)

		optimal = GridSearchCV(estimator=algorithm(), param_grid=parameters, scoring=scoring_function,\
								n_jobs=self.general_conf_['jobs'], cv=self.general_conf_['folds'])
		optimal.fit(partition.train_inputs, partition.train_outputs)

		return optimal




	def writeReport(self):

		"""


		"""

		self.results_.saveResults(self.api_path_)


