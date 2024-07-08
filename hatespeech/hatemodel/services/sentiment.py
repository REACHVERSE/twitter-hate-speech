#importing dependencies
import pandas as pd
import re
from matplotlib import style
style.use('ggplot')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import GridSearchCV
import warnings
warnings.filterwarnings('ignore')
import pickle

import os
project_root = os.getenv('PROJECT_ROOT')

#df = pd.read_csv(r'/workspaces/codespaces-blank/hatespeech/twitter_parsed_dataset.csv')
df = pd.read_csv(os.path.join(project_root, 'hatespeech','twitter_parsed_dataset.csv'))
df = df.dropna()

#defining a function to clean text
def clean(text):
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text, flags = re.MULTILINE)
    test = re.sub(r"\@w+|\#", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    tweet_tokens = word_tokenize(text)
    text = [word for word in text.split(" ") if word not in stop_words]
    text = " ".join(text)
    return text

#applying the cleaning function
df.Text = df["Text"].apply(clean)

#initialising lemmatiser
lemmatizer = WordNetLemmatizer()
def lemmatizing(data):
    tweet = [lemmatizer.lemmatize(w) for w in data]
    return data

df['Text'] = df['Text'].apply(lambda x: lemmatizing(x))

#initialising the vectoriser with a trigram language model
vect2 = TfidfVectorizer(ngram_range=(1,3)).fit(df['Text'])

feature_names = vect2.get_feature_names_out()
#print("Number of features: {} \n".format(len(feature_names)))
#print("First 20 features: \n{}".format(feature_names[0:20]))

X = vect2.transform(df['Text'])
Y = df['oh_label']

#oversampling the existing data with ADASYN
from imblearn.over_sampling import ADASYN
X_resampled, y_resampled = ADASYN().fit_resample(X, Y) # Now X_resampled and y_resampled contain the oversampled data

#dividing the data into training and testing data
x_train, x_test, y_train, y_test = train_test_split(X_resampled,y_resampled, test_size = 0.2, random_state = 42)

"""#Implementing the Logistic Regression Model
logreg = LogisticRegression(penalty = 'l2', C = 1.0) #enforcing data regularisation with the penalty argument set to L2
logreg.fit(x_train, y_train)
logreg_predict = logreg.predict(x_test)
logreg_acc = accuracy_score(logreg_predict, y_test)
print("The model's accuracy is {: .2f}".format(logreg_acc*100))

print(confusion_matrix(y_test, logreg_predict))
print("\n")
print(classification_report(y_test, logreg_predict))
"""
"""#implementing Logistic regression model with hyperparameter tuning with GridSearchCV
param_grid = {'C':[100, 10, 1.0, 0.1, 0.01], 'solver':['newton-cg', 'lbfgs', 'liblinear']}
grid = GridSearchCV(LogisticRegression(), param_grid, cv = 5)
grid.fit(x_train, y_train)
print("Best cross-validation score: {:.2f}\n".format(grid.best_score_))
print("Best parameters: {}".format(grid.best_params_))
"""

"""y_pred = grid.predict(x_test)
grid_acc = accuracy_score(y_pred, y_test)
print("Test accuracy: {:.2f}%".format(grid_acc*100))

print(confusion_matrix(y_test, y_pred))
print('\n')
print(classification_report(y_test, y_pred))

# Export the Trained Model using Pickle
pickle.dump(grid, open('ml_model.pkl', 'wb'))"""

#model = pickle.load(open('/workspaces/codespaces-blank/hatespeech/hatemodel/services/savedmodel.pkl', 'rb'))
model = pickle.load(open(os.path.join(project_root, 'hatespeech','hatemodel','services','savedmodel.pkl'),'rb'))
accuracy = accuracy_score(model.predict(x_test), y_test)*100