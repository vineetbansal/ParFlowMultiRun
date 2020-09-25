#%% [markdown]

# # Decision Trees and Random Forests
# ### Evaluting Parflow Only Runs to Evaluate impact of model vertical and lateral discretization


#%%
import pandas as pd

# sklearn tools we'll need
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


#%% [markdown]

# ## Import & Clean Up ParFlow Run Data - Previous Merged with run parameters

#%%

# import data
fn = 'Input/MergedTotRec_wRunPar.csv'
inData = pd.read_csv(fn)


#%% [markdown]

# ## Subset Data
# **'Independent' variables**: DX, GW, Rain Rate, Boussinesq Fit a <br>  
# **'Dependent' variable**: 'NZ'

# %%

# subset 'independent' variables
colSubset = ['ComputationalGrid.DX','Patch.x-lower.BCPressure.alltime.Value',
        'Patch.z-upper.BCPressure.rain.Value', 'Bous_a' ]
newColNames= ['DX','GW','RainRate', 'Bous_a']
colDict = dict(zip(colSubset,newColNames))
X = inData[colSubset]
X = X.rename(columns=colDict)

# subset DX/DY
y = inData['ComputationalGrid.NZ'].to_numpy()

print(X.head())

#%% [markdown]

# ### Starting with a very simple decision tree

#%%

# random seed
SEED = 42

# split training and test data
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,stratify=y,random_state=SEED)

# create and train decision tree
dt = DecisionTreeClassifier(max_depth=1,random_state=SEED)
dt.fit(X_train,y_train)

# predict test values and print
y_pred = dt.predict(X_test)
print('Accuracy of the simple decision tree: %.3f' % accuracy_score(y_test,y_pred))

# %% [markdown]

# so not all that accurate. <br>
# let's add some bagging to this problem

# ## Adding Bagging

#%%

from sklearn.ensemble import BaggingClassifier

dt = DecisionTreeClassifier(max_depth=1, random_state=SEED)
bc = BaggingClassifier(base_estimator=dt, n_estimators=300, oob_score=True)
bc.fit(X_train,y_train)
y_pred_bc = bc.predict(X_test)
print('Accuracy of the ensemble decision tree: %.3f' % accuracy_score(y_test,y_pred_bc))
print('OOB Accuracy of the ensemble decision tree: %.3f' % bc.oob_score_)

#%% [markdown]

# very little improvement in prediction capability <br>


# ## Check Out Some Random Forests

#%%
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_estimators=400,random_state=SEED,min_samples_leaf=4)
rf.fit(X_train,y_train)
y_pred_rf = rf.predict(X_test)
print('Accuracy of the random forest: %.3f' % accuracy_score(y_test,y_pred_rf))

#%% [markdown]

# remarkable improvement, 0.868, let's see what the imporant factors are

# %%
import matplotlib.pyplot as plt

importances_rf = pd.Series(rf.feature_importances_, index=X.columns)
sorted_importances_rf = importances_rf.sort_values()
sorted_importances_rf.plot(kind='barh',color='lightgreen')
plt.show()


# %% [markdown]

# Bous a is by far the most important <br>
# Is this important when looking at lateral scale

# %%
# reconfigure or 'dependent' and 'independent' variable sets

# subset 'independent' variables
colSubset = ['ComputationalGrid.NZ','Patch.x-lower.BCPressure.alltime.Value',
        'Patch.z-upper.BCPressure.rain.Value', 'Bous_a' ]
newColNames= ['NZ','GW','RainRate', 'Bous_a']
colDict = dict(zip(colSubset,newColNames))
X = inData[colSubset]
X = X.rename(columns=colDict)

# subset DX/DY
y = inData['ComputationalGrid.DX'].to_numpy()

print(X.head())


#%% 

# redo data split and random forest
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,stratify=y,random_state=SEED)
rf = RandomForestClassifier(n_estimators=400,random_state=SEED,min_samples_leaf=4)
rf.fit(X_train,y_train)
y_pred_rf = rf.predict(X_test)
print('Accuracy of the random forest: %.3f' % accuracy_score(y_test,y_pred_rf))


#%% [markdown]

# Random forests, at least in this configuration, are better able to predict DX than NZ.. interested, but what are the important factors here?

# ### Check out feature imporance

# %%
importances_rf = pd.Series(rf.feature_importances_, index=X.columns)
sorted_importances_rf = importances_rf.sort_values()
sorted_importances_rf.plot(kind='barh',color='lightgreen')
plt.show()
# %% [markdown]

# very similar, except, Groundwater has a more signficant impact, and NZ has even less of an impact than DX did. <br>

# ## Predicting Recession Curve
# now let's see if we can actually predict the true 'dependent variable(s)' starting with the exponetial factor, bous_a

#%%

# start by reconfiguring the indepent/dependent varaiables and train/test splitting them
# subset 'independent' variables
colSubset = ['ComputationalGrid.NZ','ComputationalGrid.DX','Patch.x-lower.BCPressure.alltime.Value',
        'Patch.z-upper.BCPressure.rain.Value']
newColNames= ['NZ','DX','GW','RainRate']
colDict = dict(zip(colSubset,newColNames))
X = inData[colSubset]
X = X.rename(columns=colDict)

# subset DX/DY
y = inData['Bous_a'].to_numpy()

# split data to training and testing set *note can't stratify because y isn't a categorical variable anymore
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=SEED)



#%% [markdown]

# ## let's train a simpler tree for comparison

#%% 

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error as MSE

dtr = DecisionTreeRegressor(max_depth=1,random_state=SEED)
dtr.fit(X_train,y_train)
y_pred = dtr.predict(X_test)
print('RMSE of the single layer decision tree: %.3f' % MSE(y_test,y_pred)**0.5)
dtr2 = DecisionTreeRegressor(max_depth=2,random_state=SEED)
dtr2.fit(X_train,y_train)
y_pred2 = dtr2.predict(X_test)
print('RMSE of the 2 layer decision tree: %.3f' % MSE(y_test,y_pred2)**0.5)

#%% [markdown]

# so adding a layer has a small performance boost

# ## Trying Random Forest

# %%

from sklearn.ensemble import RandomForestRegressor


# random forest
rf = RandomForestRegressor(n_estimators=400,random_state=SEED,min_samples_leaf=4)
rf.fit(X_train,y_train)
y_pred_rf = rf.predict(X_test)
print('RMSE of the random forest: %.3f' % MSE(y_test,y_pred_rf)**0.5)

importances_rf = pd.Series(rf.feature_importances_, index=X.columns)
sorted_importances_rf = importances_rf.sort_values()
sorted_importances_rf.plot(kind='barh',color='lightgreen')
plt.title('Random Forest Feature Importance - Predicting Bouss a')
plt.show()


#%% [markdown]

# so the decision tree shows some improvement to the RMSE
# all features have some importance, with the most importance from GW and least from DX.

# ## Few plots of results

#%%

# add to dataframe to plot
X_test['ypred'] = y_pred_rf
X_test['ytest'] = y_test

for value,group in X_test.groupby(['NZ']):
        plt.scatter(group['ytest'],group['ypred'],label=value,alpha=0.2)

#plt.xlabel("Leprechauns")
#plt.ylabel('Bous a Predicted')
plt.legend()
plt.show()


#%% 

# zoom in closer

for value,group in X_test.groupby(['NZ']):
        plt.scatter(group['ytest'],group['ypred'],label=value,alpha=0.2)
plt.xlim(0,15)
plt.ylim(0,15)
plt.xlabel=('Bous a Fit')
plt.ylabel=('Bous a Predicted')
plt.legend()
plt.show()

#%%

# ### Importance of GW?
# %%

for value,group in X_test.groupby(['GW']):
        plt.scatter(group['ytest'],group['ypred'],label=value,alpha=0.2)
plt.xlim(0,15)
plt.ylim(0,15)
plt.xlabel=('Bous a Fit')
plt.ylabel=('Bous a Predicted')
plt.legend()
plt.show()

# %%


for value,group in X_test.groupby(['GW']):
        plt.scatter(group['ytest'],group['ypred'],label=value,alpha=0.2)
plt.legend()
plt.show()

#%% [markdown]

# Reanalyze for well fitting data

# %% [markdown]

# Reanalyze and throw out variables with bad R2 values
r2limit = 0.95 # minimum rsquared fit parameter

goodData = inData[inData['Bous_Rsq'] > r2limit]

print(str(len(goodData)) + ' Good Data Points out of '+str(len(inData)) + ' total data points')

# start by reconfiguring the indepent/dependent varaiables and train/test splitting them
# subset 'independent' variables
colSubset = ['ComputationalGrid.NZ','ComputationalGrid.DX','Patch.x-lower.BCPressure.alltime.Value','Patch.z-upper.BCPressure.rain.Value']
newColNames= ['NZ','DX','GW','RainRate']
colDict = dict(zip(colSubset,newColNames))
X = goodData[colSubset]
X = X.rename(columns=colDict)

# subset DX/DY
y = goodData['Bous_a'].to_numpy()

# split data to training and testing set *note can't stratify because y isn't a categorical variable anymore
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=SEED)

# %%
#%% [markdown]

# ## let's train a simpler tree for comparison

#%% 

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error as MSE

dtr = DecisionTreeRegressor(max_depth=1,random_state=SEED)
dtr.fit(X_train,y_train)
y_pred = dtr.predict(X_test)
print('RMSE of the single layer decision tree: %.3f' % MSE(y_test,y_pred)**0.5)
dtr2 = DecisionTreeRegressor(max_depth=2,random_state=SEED)
dtr2.fit(X_train,y_train)
y_pred2 = dtr2.predict(X_test)
print('RMSE of the 2 layer decision tree: %.3f' % MSE(y_test,y_pred2)**0.5)

#%% [markdown]

# so adding a layer has a small performance boost

# ## Trying Random Forest

# %%

from sklearn.ensemble import RandomForestRegressor


# random forest
rf = RandomForestRegressor(n_estimators=400,random_state=SEED,min_samples_leaf=4)
rf.fit(X_train,y_train)
y_pred_rf = rf.predict(X_test)
print('RMSE of the random forest: %.3f' % MSE(y_test,y_pred_rf)**0.5)

importances_rf = pd.Series(rf.feature_importances_, index=X.columns)
sorted_importances_rf = importances_rf.sort_values()
sorted_importances_rf.plot(kind='barh',color='lightgreen')
plt.title('Random Forest Feature Importance - Predicting Bouss a')
plt.show()

#%%
# add to dataframe to plot
X_test['ypred'] = y_pred_rf
X_test['ytest'] = y_test

for value,group in X_test.groupby(['NZ']):
        plt.scatter(group['ytest'],group['ypred'],label=value,alpha=0.2)

#plt.xlabel("Leprechauns")
#plt.ylabel('Bous a Predicted')
plt.legend()
plt.show()

#%%
# add to dataframe to plot
X_test['ypred'] = y_pred_rf
X_test['ytest'] = y_test

for value,group in X_test.groupby(['DX']):
        plt.scatter(group['ytest'],group['ypred'],label=value,alpha=0.2)

#plt.xlabel("Leprechauns")
#plt.ylabel('Bous a Predicted')
plt.legend()
plt.show()


# %%

plt.scatter(X_test['ytest'],X_test['ypred'],color=X_test['RainRate'],alpha=0.2)

#plt.xlabel("Leprechauns")
#plt.ylabel('Bous a Predicted')
#plt.legend()
plt.show()
# %%
