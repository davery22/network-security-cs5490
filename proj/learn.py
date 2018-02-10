import numpy as np
import random
from sklearn import linear_model
from sklearn import ensemble

def load_data(datafile, RXno):
    print 'Loading data...'
    if not RXno in [1,2]:
        raise Exception('Invalid receiver: Choose 1 or 2')
    start,stop = [0,2] if RXno == 1 else [2,4] 
    readings = []
    with open(datafile, 'r') as data:
        for line in data.readlines():
            line = line.strip().split(',')
            missing = bool(not line[start])
            if missing:
                readings.append(None)
            else:
                readings.append(map(float, line[start:stop])) # Time and RSS of RX_#

    return readings

def extract_experiments(readings, experiment_count):
    print 'Processing data...'
    readings_per_batch = len(readings) / experiment_count
    experiment_spans = range(0, len(readings), readings_per_batch)
    experiment_spans = [[experiment_spans[i], experiment_spans[i+1]] for i in range(len(experiment_spans)-1)]
    experiments = [readings[start:stop] for start,stop in experiment_spans]

    return experiments

def featurize_interval(interval):
    maximum, minimum = float('-inf'), float('inf')
    for reading in interval:
        if reading[1] < minimum:
            minimum = reading[1]
        if reading[1] > maximum:
            maximum = reading[1]

    data = map(lambda x: (x-minimum)/(maximum-minimum), [reading[1] for reading in interval]) # [0,1] scaling

    mean = 0.0
    for reading in interval:
        mean += reading[1] # RSS measurement
    mean = mean / len(interval)

    stddev = 0.0
    for reading in interval:
        stddev += (reading[1] - mean) ** 2
    stddev = (stddev / (len(interval)-1)) ** 0.5

    return [mean, stddev]

def featurize_experiment(experiment, example_count, readings_per_example, label):
    experiment = [reading for reading in experiment if reading] # Prune missing values
    interval_spans = range(0, len(experiment), readings_per_example)
    interval_spans = [[interval_spans[i], interval_spans[i+1]] for i in range(len(interval_spans)-1)]
    intervals = [experiment[start:stop] for start,stop in interval_spans]
    examples = [featurize_interval(interval) for interval in intervals]
    labels = [label for _ in range(len(examples))]
    
    return [examples, labels]

def process_data(experiments, people_in_experiments, min_duration=30):
    print 'Featurizing experiments (Min duration: {} seconds)...'.format(min_duration)
    experiment_duration = experiments[0][-1][0] - experiments[0][0][0] # experiments[batch][reading][measurement]
    example_count = int(experiment_duration / min_duration)
    readings_per_example = min(len(experiments[0]) / example_count, len(experiments[0])-1)
    nested_data = [featurize_experiment(experiment, example_count, readings_per_example, people_in_experiments[i]) for i,experiment in enumerate(experiments)]
    examples = []
    labels = []

    for data in nested_data:
        examples += data[0]
        labels += data[1]

    return np.array(examples), np.array(labels)

def print_decision_matrix(predictions, test):
    length = max(max(predictions),max(test[1])) + 1
    labels = [[0 for _ in range(length)] for _ in range(length)]
    true_labels = list(set(test[1]))
    for i,pred in enumerate(predictions):
        labels[test[1][i]][pred] += 1
            
    print '  ',
    for i in range(length):
        print '{: >2}'.format(i),
    print
    print
    for i,label in enumerate(labels):
        print '{: <2}'.format(i),
        for count in label:
            print '{: >2}'.format(count),
        print
    print


def evaluate_model(model, test, accuracy_range=3):
    predictions = model.predict(test[0])
    predictions = map(lambda x: int(round(x)), predictions) # convert to ordinals

    #print test[1]
    #print predictions

    for i in range(accuracy_range+1):
        accuracy = sum([abs(x[0]-x[1]) <= i for x in zip(predictions, test[1])]) / float(len(test[1]))
        print 'Accuracy (within {} people): {}'.format(i, accuracy)
    
    print_decision_matrix(predictions, test)

    #print [abs(x[0]-x[1]) for x in zip(predictions, test[1])]

def main():
    # Set parameters
    RXno = 1
    people_in_experiments = [0,1,2,3,4,5,7,9]
    new_experiment_duration = 10 # No more than 240 (240 seconds = 4 min = the original experiment durations)
    datafile = './data/RSS_2tx.txt'

    # Load and prepare the data
    readings = load_data(datafile, RXno=RXno)
    experiments = extract_experiments(readings, len(people_in_experiments))
    examples, labels = process_data(experiments, people_in_experiments, min_duration=new_experiment_duration)

    # Shuffle the data
    shuffled = zip(examples, labels)
    random.shuffle(shuffled)
    examples, labels = zip(*shuffled)

    # Split train and test
    train_test = 0.5 # percentage of data to use for training
    bound = int(len(examples)*train_test)
    train, test = [examples[:bound], labels[:bound]], [examples[bound:], labels[bound:]]

    # Train a model
    regressor = ensemble.GradientBoostingRegressor() # default hyper-parameters
    regressor.fit(*train)

    # Evaluate train and test accuracy
    accuracy_range = 3
    print 'Train:'
    evaluate_model(regressor, train, accuracy_range)
    print 'Test:'
    evaluate_model(regressor, test, accuracy_range)


if __name__ == '__main__':
    main()
