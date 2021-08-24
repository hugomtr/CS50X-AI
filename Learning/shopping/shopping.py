import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    month = ['Jan','Feb','Mar','Apr','May','June','Jul','Aug','Sep','Oct','Nov','Dec']

    with open("shopping.csv") as f:
        reader = csv.reader(f)
        next(reader)
        evidence = []
        label = []
        for row in reader:
            evidence.append([cell for cell in row[:-1]])
            label.append(1 if row[-1] == 'TRUE' else 0)

        for row in evidence:
            for i in range(len(row)):
                if i<5 and i%2 == 0:
                    row[i] = int(row[i])
                elif i<5 and i%2 != 0:
                    row[i] = float(row[i])
                elif i>=5 and i<= 9:
                    row[i] = float(row[i])
                elif i == 10:
                    row[i] = month.index(row[i])
                elif i>=11 and i<=14:
                    row[i] = int(row[i])
                elif i == 15:
                    if row[i] == 'New_Visitor':
                        row[i] = 0
                    else:
                        row[i] = 1
                elif i == 16:
                    if row[i]:
                        row[i]=1
                    else:
                        row[i]=0

    return evidence,label

def train_model(evidence, labels):
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model

def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    tn, fp, fn, tp = confusion_matrix(labels, predictions).ravel()
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    return sensitivity, specificity


if __name__ == "__main__":
    main()
