from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
URL = r'https://raw.githubusercontent.com/rostro36/Vernehmlassungen/master/laws.csv'
df = pd.read_csv(URL)

df.head(100)


df = df.dropna(
    subset=['SR_Links', 'Months_until_accept', 'Months_until_decision'])
no_text = df.drop(columns=['Title', 'Text', 'Unnamed: 0', 'index', 'index.1', 'SR_Links',
                  'SR_Numbers', 'Months_until_accept', 'Accept_day', 'Accept_month', 'Accept_year']).reset_index()
encoder = OneHotEncoder(sparse=False)
encoded = encoder.fit_transform(no_text[['Behoerde', 'Department']])
encoded = pd.DataFrame(encoded, columns=encoder.get_feature_names_out())
no_text = no_text.drop(columns=['Behoerde', 'Department', 'index'])
no_text = pd.concat([no_text, encoded], axis=1)
no_text.tail()


targets = no_text['Months_until_decision']
features = no_text.drop(columns=['Months_until_decision'])
scaler = StandardScaler()
features = scaler.fit_transform(features)
features_training, features_test, targets_training, targets_test = train_test_split(
    features, targets, test_size=0.2, random_state=42)

parameters = {'kernel': ('linear', 'poly', 'rbf',
                         'sigmoid'), 'C': [0.1, 1, 10]}
clf = GridSearchCV(SVR(), parameters, n_jobs=-1, cv=5,
                   verbose=3, scoring='neg_mean_squared_error')
clf.fit(features_training, targets_training)
predicted_test = clf.predict(features_test)
print(mean_squared_error(targets_test, predicted_test))


tf.random.set_seed(12)
for learning_rate in [1, 0.1, 0.001, 0.0001]:
    model = keras.Sequential([keras.layers.Dense(10, activation='ReLU', input_shape=(
        24,)), keras.layers.Dropout(0.1), keras.layers.Dense(1, activation='ReLU')])
    model.build()
    model.compile(optimizer=tf.optimizers.Adam(
        learning_rate=learning_rate), loss='mean_squared_error')
    model.fit(features_training, targets_training, batch_size=1, epochs=10)
    predicted_test = model.predict(features_test)
    print(learning_rate)
    print(mean_squared_error(targets_test, predicted_test))


targets = no_text['Months_until_decision']
features = no_text.drop(columns=[
                        'Months_until_decision', 'Decision_day', 'Decision_month', 'Decision_year'])
scaler = StandardScaler()
features = scaler.fit_transform(features)
features_training, features_test, targets_training, targets_test = train_test_split(
    features, targets, test_size=0.2, random_state=42)

parameters = {'kernel': ('linear', 'poly', 'rbf',
                         'sigmoid'), 'C': [0.1, 1, 10]}
clf = GridSearchCV(SVR(), parameters, n_jobs=-1, cv=5, verbose=3)
clf.fit(features_training, targets_training)
print('SVM')
print(clf.best_params_)
predicted_test = clf.predict(features_test)
print(mean_squared_error(predicted_test, targets_test))


parameters = {'max_depth': (3, 6, 12, 25, None), 'min_samples_leaf': [1, 3, 7]}
clf = GridSearchCV(DecisionTreeRegressor(random_state=12),
                   parameters, n_jobs=-1, cv=5, verbose=3)
clf.fit(features_training, targets_training)
print('Tree')
print(clf.best_params_)
predicted_test = clf.predict(features_test)
print(mean_squared_error(predicted_test, targets_test))


parameters = {'n_neighbors': (3, 5, 7, 11), 'weights': ['uniform', 'distance']}
clf = GridSearchCV(KNeighborsRegressor(), parameters,
                   n_jobs=-1, cv=5, verbose=4)
clf.fit(features_training, targets_training)
print('Nearest Neighbour')
print(clf.best_params_)
predicted_test = clf.predict(features_test)
print(mean_squared_error(predicted_test, targets_test))


parameters = {'n_estimators': (10, 50, 100), 'max_depth': (
    3, 6, 12, 25, None), 'min_samples_leaf': [1, 3, 7]}
clf = GridSearchCV(RandomForestRegressor(random_state=12),
                   parameters, n_jobs=-1, cv=5, verbose=4)
clf.fit(features_training, targets_training)
print('Random Forest')
print(clf.best_params_)
predicted_test = clf.predict(features_test)
print(mean_squared_error(predicted_test, targets_test))


parameters = {'learning_rate': (0.001, 0.01, 0.1, 0.4), 'n_estimators': (
    10, 50, 100), 'max_depth': (3, 6, 12, 25, None), 'min_samples_leaf': [1, 3, 7]}
clf = GridSearchCV(GradientBoostingRegressor(random_state=12),
                   parameters, n_jobs=-1, cv=5, verbose=4)
clf.fit(features_training, targets_training)
print('Boosting')
print(clf.best_params_)
predicted_test = clf.predict(features_test)
print(mean_squared_error(predicted_test, targets_test))


for learning_rate in [1, 0.1, 0.001, 0.0001]:
    tf.random.set_seed(12)
    model = keras.Sequential([keras.layers.Dense(10, activation='ReLU', input_shape=(
        21,)), keras.layers.Dropout(0.1), keras.layers.Dense(1, activation='ReLU')])
    model.build()
    model.compile(optimizer=tf.optimizers.Adam(
        learning_rate=learning_rate), loss='mean_squared_error')
    model.fit(features_training, targets_training, batch_size=1, epochs=10)
    predicted_test = model.predict(features_test)
    print(learning_rate)
    print(mean_squared_error(targets_test, predicted_test))


model = TFBertModel.from_pretrained('bert-base-german-cased')


df = df.dropna(
    subset=['SR_Links', 'Months_until_accept', 'Months_until_decision'])
text = df.drop(columns=['Unnamed: 0', 'index', 'index.1', 'SR_Links', 'SR_Numbers',
               'Months_until_accept', 'Accept_day', 'Accept_month', 'Accept_year']).reset_index()
encoder = OneHotEncoder(sparse=False)
encoded = encoder.fit_transform(text[['Behoerde', 'Department']])
encoded = pd.DataFrame(encoded, columns=encoder.get_feature_names_out())

tokenizer = BertTokenizer.from_pretrained('bert-base-german-cased')
inputs = tokenizer(text['Title'].to_list(), return_tensors='tf', padding=True)
embedded_title = model(inputs)
embedded_title = pd.DataFrame(embedded_title['pooler_output'].numpy())


def no_nan(input):
    if type(input) == float:
        return ""
    return input


checked_text = [no_nan(input) for input in text['Text']]
tokenizer = BertTokenizer.from_pretrained('bert-base-german-cased')
concat_text = None
len_text = len(text)
for i in range(50):
    inputs = tokenizer(checked_text[int(
        i*len_text/50):int((i+1)*len_text/50)], return_tensors='tf', padding=True, truncation=True)
    embedded_text = model(inputs)
    embedded_text = embedded_text['pooler_output'].numpy()
    print(i)
    if concat_text is None:
        concat_text = embedded_text
    else:
        concat_text = np.concatenate([concat_text, embedded_text])
embedded_text = pd.DataFrame(concat_text)


text = text.drop(columns=['Behoerde', 'Department', 'index', 'Title', 'Text'])
text = pd.concat([text, encoded, embedded_title, embedded_text], axis=1)
text.tail()


targets = text['Months_until_decision']
features = text.drop(columns=['Months_until_decision',
                     'Decision_day', 'Decision_month', 'Decision_year'])
scaler = StandardScaler()
features = scaler.fit_transform(features)

features_training, features_test, targets_training, targets_test = train_test_split(
    features, targets, test_size=0.2, random_state=42)

parameters = {'kernel': ('linear', 'poly', 'rbf',
                         'sigmoid'), 'C': [0.1, 1, 10]}
clf = GridSearchCV(SVR(), parameters, n_jobs=-1, cv=5, verbose=3)
clf.fit(features_training, targets_training)
print('SVM')
print(clf.best_params_)
predicted_test = clf.predict(features_test)
print(mean_squared_error(predicted_test, targets_test))

parameters = {'max_depth': (3, 6, 12, 25, None), 'min_samples_leaf': [1, 3, 7]}
clf = GridSearchCV(DecisionTreeRegressor(random_state=12),
                   parameters, n_jobs=-1, cv=5, verbose=3)
clf.fit(features_training, targets_training)
print('Tree')
print(clf.best_params_)
predicted_test = clf.predict(features_test)
print(mean_squared_error(predicted_test, targets_test))

for learning_rate in [1, 0.1, 0.001, 0.0001]:
    tf.random.set_seed(12)
    model = keras.Sequential([keras.layers.Dense(10, activation='ReLU', input_shape=(
        1557,)), keras.layers.Dropout(0.1), keras.layers.Dense(1, activation='ReLU')])
    model.build()
    model.compile(optimizer=tf.optimizers.Adam(
        learning_rate=learning_rate), loss='mean_squared_error')
    model.fit(features_training, targets_training, batch_size=1, epochs=10)
    predicted_test = model.predict(features_test)
    print(learning_rate)
    print(mean_squared_error(targets_test, predicted_test))
