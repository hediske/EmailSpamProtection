# -*- coding: utf-8 -*-
"""logistic regression mail spam detection system.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1_CXZpOcq6VgCuQnI9FIjZkcWaN8wSl0I
"""

import matplotlib as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report,precision_score
import pickle

"""We need to load the data now"""

data = pd.read_csv('./data/spam.csv')

data.fillna(" ",inplace=True)

"""

```
we can check the frist 5 mails
```

"""

data.head()

data.shape

data.loc[data['Category'] == 'ham' , 'Category'] = 1
data.loc[data['Category'] == 'spam' , 'Category'] = 0

data.head()

ham_count = data[data['Category'] == 1].shape[0]
total_count = data.shape[0]
ham_percentage = (ham_count / total_count) * 100

print(ham_percentage)

"""Now the data is prepared we can create our model"""

X= data['Message']

Y = data['Category']

X_train , X_test , Y_train , Y_test = train_test_split(X,Y,train_size=0.8,random_state=3)

print(X_train.shape)
print(X_test.shape)
print(Y_train.shape)
print(Y_test.shape)

vectorizer = TfidfVectorizer(lowercase=True,min_df=1,stop_words='english')
X_train_vect = vectorizer.fit_transform(X_train)
X_test_vect = vectorizer.transform(X_test)
Y_train = Y_train.astype('int')
Y_test = Y_test.astype('int')


"""Now we will create the model !"""

model = LogisticRegression(class_weight='balanced')

model.fit(X_train_vect, Y_train)

prediction_on_trained = model.predict(X_train_vect)
accuracy_on_trained = accuracy_score(Y_train,prediction_on_trained)

prediction_on_tested = model.predict(X_test_vect)
accuracy_on_tested = accuracy_score(Y_test,prediction_on_tested)

print(accuracy_on_tested)
print(accuracy_on_trained)

#Precisition calculation
precision = precision_score(Y_train,prediction_on_trained)

print(precision)

print(classification_report(Y_test, prediction_on_tested))



with open("models/logistic_regression.pkl","wb") as model_file:
    pickle.dump(model,model_file)

with open("models/tfid_vectorizer.pkl","wb") as vectorizer_file:
    pickle.dump(vectorizer,vectorizer_file)


