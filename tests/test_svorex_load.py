from sys import path as syspath
from os import path as ospath

import unittest

import numpy as np
from sklearn.model_selection import GridSearchCV
import ntpath

syspath.append(ospath.join('..', 'classifiers'))

from SVOREX import SVOREX


class TestSvorexLoad(unittest.TestCase):
	"""
	Class testing SVOREX's functionality.

	This classifier is built in classifiers/SVOREX.py.
	"""
		
	def test_redsvm_load(self):
		
		print("\n")
		print("++++++++++++++++")
		print("SVOREX load test")
		print("++++++++++++++++")
		print()

		datasets_names = ["test_datasets/test_redsvm_svorex_load_dataset/train_automobile.0", 
						"test_datasets/test_redsvm_svorex_load_dataset/train_balance-scale.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_bondrate.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_car.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_contact-lenses.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_ERA.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_ESL.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_eucalyptus.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_LEV.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_newthyroid.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_pasture.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_squash-stored.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_squash-unstored.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_SWD.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_tae.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_toy.0",
						"test_datasets/test_redsvm_svorex_load_dataset/train_winequality-red.0"]

		classifiers = [SVOREX(kernel_type=0)]

		parameters = {'c': np.full(7,10.)**np.arange(-3,4), 'k': np.full(7,10.)**np.arange(-3,4)}
		
		for dataset_name in datasets_names:
			dataset = np.loadtxt(dataset_name)

			X_train = dataset[:,0:(-1)]
			y_train = dataset[:,(-1)]
			
			print("-------------")
			print("Dataset {}...".format(ntpath.basename(dataset_name)))

			for classifier in classifiers:
				grid = GridSearchCV(classifier, parameters, n_jobs=-1, cv=3)
				grid.fit(X_train, y_train)

			print("Done!")


if __name__ == '__main__':
	unittest.main()