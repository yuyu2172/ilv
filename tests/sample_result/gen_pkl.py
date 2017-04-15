import datetime
import pickle


with open('directory_1/settings.pkl', 'wb') as f:
    logs = {
        'create_time': '2017-02-03',
        'message': 'Test'
    }
    pickle.dump(logs, f)

with open('directory_2/settings.pkl', 'wb') as f:
    logs = {
        'create_time': '2017-02-08',
        'message': 'Test'
    }
    pickle.dump(logs, f)
