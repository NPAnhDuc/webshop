"""One-day-ahead forecasting experiment; synthetic data only, not a shop forecast.

Train Oct-May, validation Jun-Jul, frozen test Aug-Sep. Features use yesterday
or earlier. Test is evaluated once after selecting by validation WAPE. Real past
test observations become available between successive one-day predictions; this
does NOT estimate a 60-day fixed-origin forecast.
"""
import argparse
import json
from pathlib import Path
import pickle


def main():
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.metrics import mean_absolute_error
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='.')
    args=parser.parse_args();root=Path(args.root)
    out=root/'outputs/forecast';out.mkdir(parents=True,exist_ok=True)
    frame=pd.read_csv(root/'data/daily_demand.csv',parse_dates=['day']).sort_values('day').set_index('day')
    y=frame['units_sold'].astype(float)
    features=pd.DataFrame(index=frame.index)
    features['weekday']=frame.index.dayofweek
    for lag in (1,7,14,28): features[f'lag_{lag}']=y.shift(lag)
    for window in (7,28): features[f'rolling_{window}']=y.shift(1).rolling(window).mean()
    features=features.dropna();target=y.loc[features.index]
    train=features.index<'2026-06-01'
    validation=(features.index>='2026-06-01')&(features.index<'2026-08-01')
    test=features.index>='2026-08-01'
    def metrics(actual,predicted):
        return {'mae':float(mean_absolute_error(actual,predicted)),
                'wape':float(np.abs(actual-predicted).sum()/np.abs(actual).sum()) if np.abs(actual).sum() else None}
    baseline_validation=metrics(target[validation],features.loc[validation,'lag_7'])
    results=[];models=[]
    for leaves in (7,15):
        model=HistGradientBoostingRegressor(max_leaf_nodes=leaves,max_iter=100,
              min_samples_leaf=20,learning_rate=.05,random_state=42)
        model.fit(features[train],target[train])
        score=metrics(target[validation],np.maximum(0,model.predict(features[validation])))
        results.append({'max_leaf_nodes':leaves,**score});models.append(model)
    index=min(range(len(results)),key=lambda i:results[i]['wape'])
    selected='weekly_naive';model=None
    if results[index]['wape']<baseline_validation['wape']:
        selected='hist_gradient_boosting';model=models[index]
    baseline_test=features.loc[test,'lag_7'].to_numpy()
    predictions=baseline_test if model is None else np.maximum(0,model.predict(features[test]))
    report={'data_kind':'synthetic','target':'gross sold units per day; not net returned units',
            'horizon':'one day ahead, rolling observed history',
            'train_end':'2026-05-31','validation':['2026-06-01','2026-07-31'],'test':['2026-08-01','2026-09-30'],
            'samples':{'train':int(train.sum()),'validation':int(validation.sum()),'test':int(test.sum())},
            'validation_baseline':baseline_validation,'validation_candidates':results,'selected_model':selected,
            'test_selected':metrics(target[test],predictions),'test_weekly_naive':metrics(target[test],baseline_test),
            'deployment_approved':False,
            'limitations':['Only one synthetic annual cycle; no evidence of real-world accuracy.',
                           'Realized sales are censored by stockouts; not a forecast of unconstrained demand.',
                           'No claim that marketing or seasonality effects were causally identified.',
                           'Forecast intervals and multi-day forecasts have not been validated.']}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    # Only load this locally-produced artifact, never arbitrary downloaded pickle files.
    with (out/'candidate.pkl').open('wb') as stream:
        pickle.dump({'kind':selected,'model':model,'feature_columns':list(features.columns),'report':report},stream)
    pd.DataFrame({'day':features.index[test],'actual':target[test].to_numpy(),
                  'predicted':predictions,'weekly_naive':baseline_test}).to_csv(out/'test_predictions.csv',index=False)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__': main()
