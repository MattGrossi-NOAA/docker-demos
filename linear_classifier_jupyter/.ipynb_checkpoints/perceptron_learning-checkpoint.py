# TO CONVERT TO FUNCTION:
# - Function(data to fit, target classes, train percentage, initial weights, learning rate)
# - Edit indexing to accomodate user-specified class
# - Add training/testing subsets
# - Add testing routine at the end (run classifier on each testing example, record and report error)

"""
perceptron_learning.py

Author: Matt Grossi (matthew.grossi at rsmas.miami.edu)
Created: 2018-Feb-27

A script to train and test a linear classifier using the perceptron learning
method.

Data are read in, normalized and divided into training and testing subsets.
Initial weights are randomly defined by user. This script trains a w0 weight
(sometimes referred to as the threshold) and therefore requires the user to
provide n+1 weights, where n is the number of attributes.

When run, the epoch number, cumulative training example number, and error
rates are printed to the screen. Training stops when the error rate drops
below the user-defined error limit for one complete epoch.

"""

# LOAD packages and data
import numpy as np
import random

data = np.loadtxt(fname='banknote_authentification.csv', delimiter=',')

# NORMALIZE Data
MAX = data.max(axis=0)
MIN = data.min(axis=0)
norm = (data - MIN) / (MAX - MIN)

# Append attribute x0=1 (used for weight-training)
norm = np.append(arr=np.ones([len(norm),1]), values=norm, axis=1)

# DEFINE learning rate and weights
lr = 0.3

# Weights (randomly initialized)
w0 = 0.1
w1 = 0.3
w2 = 0.5
w3 = 0.2
w4 = 0.4
weights = [w0, w1, w2, w3, w4]

# ARCHIVE weight progression
# When defining a duplicate or backup variable, include [:] at the end of the variable to prevent mutability/changes
weights_archive = weights[:];

# Function to adjust weights:

def adjust(weight, att, tar, hyp, eta):
    """
    Returns adjusted weight(s) based on the learning rate, corresponding attribute value(s), and the
    difference between the known and hypothesized class.
    
    Inputs: weight - weight(s) to be adjusted, att - corresponding attribute(s), tar - known class
    (from data; i.e., the 'target'), hyp - hypothesized class (from classifier), eta - learning rate
    Outputs: aw - adjusted weight(s)
    """
    aw = weight + (eta * (tar - hyp) * att);

    return aw


# CONDITIONS to continue loops

# Column in 'data' containing known classification (assumed to be the last column)
class_col = np.shape(data)[1];

# Performance flag: Did the classifier correctly classify the training example? (1=incorrect, 0=correct)
check = np.ones([len(norm),1]);

# Epoch and training example counters
num_epoch = 0;
num_ex = 0;

# Record percent error as each training example is presented
pct_error = [];

# WHILE LOOP: Starts new epochs, as needed. Stop when the error rate remains below the user-defined error limit for an entire epoch.
# FOR LOOP: Presents training examples one by one, adjusts weights as needed, sets 'Performance Flag' as appropriate

while sum(check) != 0:
    # Update epoch counter
    num_epoch += 1;
    for ex in np.arange(start=0,stop=len(norm),step=1):
        # If at least one training example was incorrect classified, continue
        if sum(check) != 0:
            # Extract target class
            c = int(norm[ex,class_col]);
            # Output of linear classifier (w0x0 + w1x1 + ... + w4x4)
            out = sum(weights * norm[ex,0:class_col])
            # If the output is >0, choose hypothesized class to be 1; otherwise, choose class 0
            if out > 0:
                h = 1
            else:
                h = 0
            # If the hypthesized class is not the same as the correct class, adjust weights, add new weights to 'weights_archive', and set 'Performance Flag' to 1; otherwise, preserve weights and set 'Performance Flag' to 0.
            if c-h != 0:
                weights = adjust(weight=weights,att=norm[ex,0:class_col],tar=c,hyp=h,eta=lr);
                weights_archive = np.row_stack((weights_archive,weights))
                check[ex] = 1;
            else:
                check[ex] = 0;
            # Update training example counter
            num_ex += 1;
            # Check percent error
            pct_error = np.append(pct_error,(sum(check)/len(norm))*100);
            # Print info to screen
            print('Epoch: ' + str(num_epoch) + ' - Example: ' + str(num_ex) + ' - Percent Error: ' + str(pct_error[num_ex-1]));
            # Extract error rates for last epoch
            err_ind = pct_error[len(pct_error)-len(norm):len(pct_error)];
            # Stop if at least one entire epoch has been completed AND the error rate is below the user-defined error limit for one full epoch
            if len(pct_error) >= len(norm) and sum(err_ind > 0.3)==0:
                check = np.zeros([len(norm),1]);
