import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from datetime import datetime

# df = pd.read_csv('sounding.csv', names= cnames, header=0)

def computeForecast(df):
    # Altitude in feet
    df['ALT'] = df.HEIGHT*3.28084

    # Convert from T in 10th of degrees celcius
    df.TEMP=df.TEMP/10
    df.DEWPT=df.DEWPT/10

    df['SPREAD'] = df.TEMP - df.DEWPT
    df['VIRTT'] = (df.TEMP + 273.15)/(1 - 0.379*(6.11*10*((7.5*df.DEWPT)/(237.7+df.DEWPT)))/df.PRESSURE)-273.15

    # DALR, T.I.
    max_t = df.iloc[0,3]
    df['DALR'] = max_t - df.HEIGHT/1000*9.8
    df['TI'] = df.VIRTT - df.DALR

    # Scorer
    df['TK'] = df.TEMP+273.15
    df['Y'] = (df.TEMP-df.TEMP.shift(-1))/(df.HEIGHT.shift(-1)-df.HEIGHT)
    df['WV_MPS'] = df.WIND_SPD*0.514
    df['L2'] = (((0.00986-df.Y)/df.TK)*(9.81/pow(df.WV_MPS,2))-(1/4)*pow(((9.81/287-df.Y)/df.TK),2))*100000
    
    return df

def processSummary(col, sdfs, hour):
    dfs = pd.DataFrame()
    for sdf in sdfs:
        dfs['ALT'] = sdf['ALT']
        dfs['UTC_' + str(hour)] = sdf[col]
        hour = hour + 1
    return dfs

def numberToLetters(q):
    q = q - 1
    result = ''
    while q >= 0:
        remain = q % 26
        result = chr(remain+65) + result;
        q = q//26 - 1
    return result

def uploadToGoogle(df, sheet):
    # Upload the results to Google Drive
    #json_key = json.load(open('flightbit-key.json'))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('flightbit-key.json', scope)

    gc = gspread.authorize(credentials)

    wb = gc.open_by_key('1q8YhqClfmTF_be4QnqgDGMqJfDj_ELdQSrrjlqPb770')
    ws = wb.worksheet(sheet)

    # columns names
    columns = df.columns.values.tolist()
    # selection of the range that will be updated
    cell_list = ws.range('A1:'+numberToLetters(len(columns))+'1')
    # modifying the values in the range
    for cell in cell_list:
        val = columns[cell.col-1]
        if type(val) is str:
            val = val.decode('utf-8')
        cell.value = val
    # update in batch
    ws.update_cells(cell_list)

    # number of lines and columns
    num_lines, num_columns = df.shape
    # selection of the range that will be updated
    cell_list = ws.range('A2:'+numberToLetters(num_columns)+str(num_lines+1))
    # modifying the values in the range
    for cell in cell_list:
        val = df.iloc[cell.row-2,cell.col-1]
        if type(val) is str:
            val = val.decode('utf-8')
        elif isinstance(val, (int, long, float, complex)):
            # note that we round all numbers
            val = val
        cell.value = val
    # update in batch
    ws.update_cells(cell_list)

    
cnames = ["TYPE","PRESSURE","HEIGHT","TEMP","DEWPT","WIND_DIR","WIND_SPD"]

now = datetime.now(tz=pytz.utc)

df = pd.read_csv('http://rucsoundings.noaa.gov/get_soundings.cgi?data_source=Op40&latest=latest&n_hrs=18&fcst_len=shortest'+
                 '&airport=kawo&text=Ascii%20text%20%28GSD%20format%29&hydrometeors=false&start=latest')

hour = int(df.iloc[0,1])

print "Start Hour (UTC): " + str(hour)

df = df[df.TYPE.isin(['4', '5', '9'])]
df = df.reset_index(drop=True)

# Find the row indexes where new soundings start
idxs = df[df['TYPE'] == '9'].index.tolist()
df[cnames] = df[cnames].astype(float)

sdfs = []

for idx, val in enumerate(idxs):
    if val != idxs[-1]:
        start = val
        end = idxs[idx+1]
        sdfs.append(df[start:end].copy().reset_index(drop=True))
    else:
        sdfs.append(df[val:].copy().reset_index(drop=True))

# Process the soundings
for sdf in sdfs:
    computeForecast(sdf)

# Generate summaries
for summary in ['TI', 'SPREAD', 'WIND_SPD', 'WIND_DIR', 'L2']:
    df_s = processSummary(summary, sdfs, hour)
    uploadToGoogle(df_s, summary)