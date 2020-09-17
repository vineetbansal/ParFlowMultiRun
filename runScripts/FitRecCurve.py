


from RecCurveModels import exponentialMshift, boussinesqshift, coutagneshift
from scipy.optimize import curve_fit
import numpy as np

def subsetRec(allSto):
    ''' subset storage data array/series for the recession period only '''

    # subset recession
    maxStoIdx = allSto.idxmax()

    recSto = allSto[maxStoIdx:]
    return recSto

def fitModel(model,xvalues,yvalues,p0s):

    # try to fit it
    try:
        popt = curve_fit(model,xvalues,yvalues,p0=p0s)[0]
        model_stats = getfitstats(model(xvalues, *popt), yvalues)
    except:
        popt = np.empty(len(p0s))
        model_stats = np.empty(3)

    return popt, model_stats

def as_csv(array):
    return ','.join([str(i) for i in array]) + '\n'

def getfitstats(yest,yData):
    absError = yest - yData
    SE = np.square(absError) # squared errors
    MSE = np.mean(SE) # mean squared errors
    RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
    Rsquared = 1.0 - (np.var(absError) / np.var(yData))
    return MSE,RMSE,Rsquared

def fitRecCurve(stoDat, outFile):

    # subset the 'rain-rec period' from the full storage data
    recSto = subsetRec(stoDat.squeeze()).to_numpy() # and convert to numpy array

    # get min and max storage
    maxSto = stoDat.max()
    minSto = stoDat.min()

    # get model optimal parameters
    recLen = len(recSto)
    xvalues = np.arange(0,recLen)
    popt_mals, stats_mals = fitModel(exponentialMshift,xvalues,recSto, [maxSto,minSto, 0.047])
    popt_boss, stats_boss = fitModel(boussinesqshift,xvalues,recSto, [maxSto,minSto, 0.036])
    popt_cous, stats_cous = fitModel(coutagneshift, xvalues, recSto, [maxSto,minSto,0.045, 1.012])

    # merge data together to write out
    mergeStats = np.concatenate([popt_mals,popt_boss,popt_cous,stats_mals,stats_boss, stats_cous])
        
    # save the data
    filehead=np.asarray(['Mal_Qo','Mal_Qf','Mal_a',
    'Bous_Qo','Bous_Qf','Bous_a',
    'Cou_Qo','Cou_Qf','Cou_a','Cou_b',
    'Mal_MSE','Mal_RMSE','Mal_Rsq',
    'Bous_MSE','Bous_RMSE','Bous_Rsq',
    'Cou_MSE','Cou_RMSE','Cou_Rsq'])

    with open(outFile,'w') as f:
        f.write(as_csv(filehead))
        f.write(as_csv(mergeStats))
