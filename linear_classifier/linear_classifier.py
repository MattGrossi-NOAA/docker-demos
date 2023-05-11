#!/usr/local/bin/python3 

"""
linear_classifier.py

Author: Matt Grossi (matt.grossi at noaa.gov)
Created: 2023-May-05
"""

import numpy as np
import warnings
import argparse
import sys

class Linear:
    """
    Embarrassingly simple linear classifier using perceptron learning.
    
    Initialization inputs:
        data: str, fileneame of CSV data to be trained on, organized with row-wise 
            examples and column-wise attributes. Known classes are expected to be in 
            the last column.
        train: float, 0 < train < 1, specifies the fraction of data to be used for
            training. Defaults to 0.75.
        threshold: float, 0 < threshold < 1, the accuracy threshold above which the 
            model is considered adequate and training stops. Defaults to 0.9.
        lr: float, learning rate used to adjust weights during training. Usually <1. 
            Defaults to 0.1
        seed: int, used to set random seed prior to weight initialization for 
            reproducibility. If not supplied, weights will be initialized 
            differently for every instantiation (default).
        max_epochs: int, maximum number of training epochs before training stops
            for non-convergence. Defaults to 100.
        verbose: Boolean controlling whether model performance status should be 
            printed during training.
    """
    def __init__(self, data, train=0.75, threshold=0.9, lr=0.1, seed=None,
                 max_epochs=100, verbose=True):
        self.dfile = data
        self.training = train
        self.threshold = threshold * 100
        self.eta = lr
        self.seed = seed
        self.max_epochs = max_epochs
        self.verbose = verbose
    
        # Load data
        self.data = np.loadtxt(fname=self.dfile, delimiter=',')

        # Normalize
        MAX = self.data.max(axis=0)
        MIN = self.data.min(axis=0)
        self.norm = (self.data - MIN) / (MAX - MIN)
        
        # Append artificial "zeroth" bias attribute x0=1
        # (used for weight-training)
        self.norm = np.append(arr=np.ones([len(self.norm),1]),
                              values=self.norm, axis=1)
        
        # Initialize
        self.initialize(shuffle=True)
        
    def __str__(self):
        return 'Embarrassingly simple linear classifier using perceptron learning.'
    
    def __repr__(self):
        return f'Embarrassingly simple linear classifier trained on {self.dfile}'

    def initialize(self, shuffle=True):
        """
        Randomly initialize weights.
        
        Input:
            shuffle: Boolean whether normalized data should be shuffled first. If 
                True (default), the newly shuffled data are also subset according to 
                'train' argument passed at instance initialization or as set by
                set_train_subset method.
        """
        # Shuffle examples
        if shuffle:
            print('Shuffling examples')
            self.shuffled = self.norm[:]
            np.random.shuffle(self.shuffled)

            # Training/testing subsets
            print('Splitting shuffled data into training and testing subsets')
            trainInd = round(self.training * len(self.shuffled))
            self.trainSS = self.shuffled[:trainInd]
            self.testSS = self.shuffled[trainInd:]        
    
        # Initialize weights
        wgts_rng = np.random.default_rng(seed=self.seed)
        num_weights = self.norm.shape[1] - 1
        self.weights = wgts_rng.random(num_weights)
        
    def reset(self, shuffle=True, seed=None):
        """
        Re-initialize model to random weights for retraining.
        
        Input:
            shuffle: Boolean whether normalized data should be (re)shuffled first.
                If True (default), the newly shuffled data are also subset according
                to 'train' argument passed at instance initialization or as set by
                set_train_subset method.
            seed: int, optionally set random seed prior to weight initialization. 
                Set this for reproducibility. If not supplied, seed will be retained
                from initializtion. Use str 'None' to force set to NoneType if a
                seed value was previously set, either upon initiation or with this
                'reset' method. No random seed will cause weights to be initialized
                differently every time.
        """
        if seed:
            self.set_seed(seed)
        self.initialize(shuffle=shuffle)
    
    def adjust_weights(self, att, tar, hyp):
        """
        Adjust weight(s) based on the learning rate, attribute values, and the
        difference between the known and hypothesized classes.

        Inputs:
            att: example attribute(s)
            tar: known class (from data; i.e., the 'target')
            hyp: hypothesized class (from classifier)
        """
        self.weights = self.weights + (self.eta * (tar - hyp) * att)
    
    def set_train_subset(self, fraction):
        """
        Set the fraction of data to be used for training.
        
        Input:
            fraction: float, 0 < fraction < 1
        """
        self.training = fraction
    
    def set_threshold(self, threshold):
        """
        Set the accuracy threshold above which the model is considered trained.
        
        Input:
            threshold: float, 0 < threshold < 1
        """
        self.threshold = threshold * 100
    
    def set_lr(self, lr):
        """
        Set learning rate used for training.
        
        Input:
            lr: float, usually <1
        """
        self.eta = lr
    
    def set_seed(self, seed):
        """
        Set the seed used for random weight initiation.

        Input:
            seed: int or str 'None' to force set to NoneType
        """
        if isinstance(seed, int):
            self.seed = seed
        elif isinstance(seed, str) and seed.lower() == 'none':
            self.seed = None
        else:
            raise ValueError("'seed' must be either an int or string "\
                             "string 'None' to set to NoneValue")
        warnings.warn('Random seed has been set and may be different than what was used to initiate this Linear instance.')

    def set_verbose(self, verbose):
        """
        Set whether model performance status should be printed during training.
        
        Input:
            verbose: Boolean
        """
        self.verbose = verbose
    
    def run_model(self, weights, examples):
        """
        Run linear classifier that returns 1 if the weighted sum is greater than
        zero or 0 otherwise.

        Inputs:
            weights: array of weight(s) making up the linear classifier
            examples: 2D array of examples to classify, one example per row
        """
        ws = np.sum(weights * examples, axis=1)
        h = ws > 0
        return h.astype(int)

    def get_weights(self):
        """Return existing model weights (parameters)."""
        return self.weights
    
    def accuracy(self, weights, examples):
        """
        Return the fraction of examples whose class was correctly identified.

        Inputs:
            weights: array of weight(s) making up the linear classifier
            examples: 2D array of examples to classify, one example per row
        """
        h = self.run_model(weights=weights, examples=examples[:,0:-1])
        num_correct = np.sum(examples[:,-1] == h)
        return np.round(((num_correct / len(examples)) * 100), 3)

    def error(self, weights, examples):
        """
        Return the fraction of examples whose class was incorrectly identified.

        Inputs:
            weights: array of weight(s) making up the linear classifier
            examples: 2D array of examples to classify, one example per row
        """
        h = self.run_model(weights=weights, examples=examples[:,0:-1])
        num_incorrect = np.sum(examples[:,-1] != h)
        return np.round(((num_incorrect / len(examples)) * 100), 3)

    def test(self, traindata=False):
        """
        Test the current model. Returns tuple (accuracy, error) as percentages of
        examples classified correctly and incorrectly, respectively.
        
        Input:
            traindata: Boolean indicating whether accuracy and error should be
                calculated on training subset. Defaults to False (testing subset)
        """
        ds = self.trainSS if traindata else self.testSS
        acc = self.accuracy(weights=self.weights, examples=ds)
        err = self.error(weights=self.weights, examples=ds)
        return (acc, err)
    
    def train(self):
        """Train the model"""
        if self.verbose:
            print('Training...')

        self.epoch_num = 0
        self.train_accs = []
        
        # Test initial model
        self.trainAcc, self.trainErr = self.test(traindata=True)
        self.train_accs.append(self.trainAcc)
        
        # Train
        while np.mean(self.train_accs[-3:]) < self.threshold:
            if self.verbose:
                print(f'Epoch {self.epoch_num} of {self.max_epochs} allowed: '\
                      f'Percent Error {self.trainErr}%')

            # Update epoch counter
            self.epoch_num += 1
            if self.epoch_num > self.max_epochs:
                sys.exit(f'Stopping for non-convergence after {self.max_epochs} '\
                          'max_epochs. Try increasing "max_epochs", decreasing '\
                          '"threshold", or adjusting learning rate "lr".')
                
            # Loop through each training example
            for ex in self.trainSS:
                attributes = ex[0:-1].reshape(1,-1)
                classLabel = ex[-1]
                hypothesis = self.run_model(weights=self.weights, 
                                            examples=attributes)
                self.adjust_weights(att=attributes, tar=classLabel, hyp=hypothesis)
                
            # Test current model
            self.trainAcc, self.trainErr = self.test(traindata=True)
            self.train_accs.append(self.trainAcc)

        if self.verbose:
            print(f'Epoch {self.epoch_num} of {self.max_epochs} allowed: '\
                  f'Percent Error {self.trainErr}%')
            print('Done!\n')

        # Final status
        self.testAcc, self.testErr = self.test(traindata=False)
        print(f'Final accuracy on training data: {self.trainAcc}%')
        print(f'Accuracy on testing data: {self.testAcc}%')
                        
def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Linear model control parameters.',
                 prog='linear.py', usage='%(prog)s [arguments]')
    parser.add_argument('-d', '--data', metavar='datafile', type=str,
                     help='csv file to operate on')
    parser.add_argument('-t', '--train', metavar='train', type=float, default=0.75,
                     help='Fraction of data to be used for training')
    parser.add_argument('-a', '--threshold', metavar='threshold', type=float,
                     help='Minimum acceptable accuracy for training (fraction)',
                     default=0.9)
    parser.add_argument('-l', '--lr', metavar='learnrate', 
                     help='Learning rate for weight adjustment during training',
                     type=float, default=0.01)
    parser.add_argument('-s', '--seed', metavar='seed', 
                     help='Seed for reproducibility of random initiations',
                     type=int, default=argparse.SUPPRESS)
    parser.add_argument('-m', '--max_epochs', metavar='max_epochs',
                        help='Maximum number of training epochs allowed',
                        type=int, default=100)
    parser.add_argument('-v', '--verbose', action='store_true',
                     help='Print training status after each epoch')
    return parser.parse_args()

def main():
    # Parse the user arguments
    args = parse_args()
    if 'seed' not in args:
        args.seed = None
        
    # Create and train the model
    model = Linear(data=args.data, train=args.train, threshold=args.threshold,
                   lr=args.lr, seed=args.seed, max_epochs=args.max_epochs,
                   verbose=args.verbose)
    model.train()
    
if __name__ == "__main__":
    main()
