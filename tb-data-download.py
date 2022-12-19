import click
import requests
import time
import pandas as pd
import toml
import json

from utils import getData

# # Define some information about the Thingsboard instance
# ip = 'envisim.cv.ic.ac.uk'
# port = 9090
# username = "tenant@thingsboard.org"
# password = "WMO2020"

# Experiment - get data for previous 30 days
def current_time_ms():
    """Return current time in ms since epoch."""
    return time.time_ns() // 1_000_000

def format_time_ms(time_ms, preserve_ms=False):
    """Return formatted time string."""
    s, ms = divmod(int(time_ms), 1000)  # (1236472051, 807)
    if preserve_ms:
        return '%s.%03d' % (time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(s)), ms)
    else:
        return '%s' % time.strftime('%d-%m-%Y %H:%M:%S', time.gmtime(s))

@click.command()
@click.argument('config', type=click.Path(exists=True))
def main(config):

    # From config, get:
    # - source information
    # - devices 
    config = toml.load(config)

    ip = config['source']['host']
    port = config['source']['port']
    username = config['source']['user']
    password = config['source']['password']
    
    # Perform the POST request to obtain X-Token Authorization
    r = requests.post(
        'http://' + ip + ':' + str(port) + '/api/auth/login',
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        data = '{"username":"' + username + '", "password":"' + password + '"}'
    )
    X_AUTH_TOKEN = r.json()['token']

    # get device ids (NB device type is now deprecated, so we can no longer search based on type
    # r = requests.get(
    #     "http://" + ip + ":" + str(port) + "/api/tenant/devices?type=RLMB&pageSize=10000&page=0",
    #     headers={'Accept':'application/json','X-Authorization': 'Bearer ' + X_AUTH_TOKEN}
    # )
    r = requests.get(
        "http://" + ip + ":" + str(port) + "/api/tenant/devices?pageSize=10000&page=0",
        headers={'Accept':'application/json','X-Authorization': 'Bearer ' + X_AUTH_TOKEN}
    )
    meta = r.json()['data']
    device_ids = [x['id']['id'] for x in meta if x['name'] in config['source']['devices']]
    device_nms = [x['name'] for x in meta if x['name'] in config['source']['devices']]
    endTs   = current_time_ms()
    startTs = endTs - (24 * 60 * 60 * 1000 * 100)  # 30 [100?] days ago
    
    for device, name in zip(device_ids, device_nms):
        for variable in config['source']['variables']:
            # try:
            ts = getData(
                ip=ip,
                port=port,
                user=username,
                password=password,
                deviceId=device,
                key=variable,
                startTs=str(startTs),
                endTs=str(endTs)
            )

            # Now, format data read for Anaconda
            obs = ts[variable]
            n = len(obs)
            tms = []
            vals = []
            for i in range(n):
                tm = obs[i]['ts']
                val = json.loads(obs[i]['value'])
                if hasattr(val, 'append'):
                    if len(val) > 1:
                        m = len(val)
                        tm0 = tm
                        for j in range(m):
                            val0 = val[j]
                            tms.append(format_time_ms(tm0))
                            vals.append(float(val0))
                            tm0 = tm + 300000  # 5 minutes = 300000 milliseconds
                    else:
                        tms.append(format_time_ms(tm))
                        vals.append(float(val[0]))
                else:
                    tms.append(format_time_ms(tm))
                    vals.append(float(val))

            df = pd.DataFrame({'Date': tms, 'Value': vals, 'Flag': ''})
            df.to_csv(
                name + '_' + variable + '-latest.csv',
                index=False
            )
            # except:
            #     pass
    
if __name__ == '__main__':
    main()
