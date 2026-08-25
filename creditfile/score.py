# Created 2023-10-23


from importlib_resources import files, as_file
import joblib
import lightgbm as lgb


# Artifacts
RESOURCE_LOC = files(__package__)
with as_file(RESOURCE_LOC.joinpath('artifacts/model.txt')) as eml:
    model_text = eml.read_text(encoding='utf-8').replace('\r\n', '\n')
    classifier = lgb.Booster(model_str=model_text)
with as_file(RESOURCE_LOC.joinpath('artifacts/score-scaler.pickle')) as eml:
    scaler = joblib.load(eml)


# Scorers
def predict_delinquency(features):
    'Calculate a delinquency score based on features.'
    return classifier.predict([features], raw_score=True)
    

def make_credit_score(features):
    'Calculate a credit score from 1-100.'
    delinquency_score = predict_delinquency(features)
    delinquency_score = scaler.transform([delinquency_score])[0, 0]
    credit_score = round((1-delinquency_score)*100)
    return credit_score