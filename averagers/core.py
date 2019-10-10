import datetime
import itertools
import numpy
import pandas
import ephem

def get_params_pulp(df, CDmin=0, CDmax=100, CNmin=0, CNmax=100):
    # Obsoleted
    import pulp
    CD = pulp.LpVariable('CD', CDmin, CDmax, cat='Continuous')
    CN = pulp.LpVariable('CN', CNmin, CNmax, cat='Continuous')
    newvars = list()
    for i in df.index:
        newvars.append(pulp.LpVariable('newvvar'+str(i)))
    m = pulp.LpProblem(sense=pulp.LpMinimize)
    m += pulp.lpSum( [ newvars[i] for i in df.index ] )
    for i in df.index:
        min0 = df.loc[i,'Min']
        max0 = df.loc[i,'Max']
        ave0 = df.loc[i,'Ave']
        min1 = df.loc[i,'Min_next']
        S0 = df.loc[i,'Sunset_nondimensional']
        dif = get_temp_dif(CD, CN, min0, max0, ave0, min1, S0)
        m += dif <= newvars[i]
        m += -dif <= newvars[i]
    m.solve()
    assert pulp.LpStatus[m.solve()] == 'Optimal'
    return {'CD':CD.value(), 'CN':CN.value()}

def get_average_temperature(df, params, method):
    min1 = df.loc[:,'Min']
    max1 = df.loc[:,'Max']
    min2 = df.loc[:,'Min_next']
    S1 = df.loc[:,'Sunset_nondimensional']
    if method=='DH2006':
        ave1 = ((min1+(params['CD']*(max1-min1)))*S1)+((min2+(params['CN']*(max1-min2)))*(1-S1))
    elif method=='KF':
        max0 = df.loc[:,'Max_prev']
        prop1 = (df.loc[:,'Sunrise_nondimensional'])/24
        prop2 = (df.loc[:,'Sunset_nondimensional'] - df.loc[:,'Sunrise_nondimensional'])/24
        prop3 = (24 - S1)/24
        temp1 = min1+(params['C1']*(max0-min1))
        temp2 = min1+(params['C2']*(max1-min1))
        temp3 = min2+(params['C2']*(max1-min2))
        ave1 = (temp1*prop1)+(temp2*prop2)+(temp3*prop3)
    return ave1

def get_month_average_temperature(df, mparams, method):
    df.loc[:,'Ave_simM'] = numpy.nan
    for month in mparams.keys():
        month = int(month)
        is_month = (df['Month']==month)
        ave = get_average_temperature(df.loc[is_month,:], mparams[str(month)], method=method)
        df.loc[is_month,'Ave_simM'] = ave
    return df['Ave_simM']

def get_params(df, param_min=0, param_max=10, max_step=1000, small_dif=10**-6,
               method='DH2006', num_grid=3, verbose=False):
    assert num_grid>=3, 'num_grid should be >=3.'
    if method=='DH2006':
        param_names = ['CD','CN']
    elif method=='KF':
        param_names = ['C1','C2','C3']
    param_ranges = dict()
    for pn in param_names:
        param_ranges[pn] = [param_min, param_max]
    for i in numpy.arange(1,max_step+1):
        param_units = dict()
        for pn in param_names:
            param_units[pn] = (param_ranges[pn][1]-param_ranges[pn][0])/num_grid
        if all([ v < (small_dif/num_grid) for v in param_units.values() ]):
            if verbose:
                print('Optimization completed successfully.')
            break
        param_grids = dict()
        for pn in param_names:
            if param_units[pn]<(small_dif/num_grid):
                param_grids[pn] = [(param_ranges[pn][0]+param_ranges[pn][1])/2,]
            else:
                newmin = param_ranges[pn][0]
                newmax = param_ranges[pn][1] + param_units[pn]
                param_grids[pn] = numpy.arange(newmin, newmax, param_units[pn])
        grids = list(itertools.product(*[ param_grids[k] for k in param_names ]))
        results = {'variance':[],}
        for pn in param_names:
            results[pn] = list()
        for j,grid in enumerate(grids):
            current_params = dict()
            for k,pn in enumerate(param_names):
                current_params[pn] = grid[k]
                results[pn].append(grid[k])
            ave = get_average_temperature(df, current_params, method)
            var = (((ave-df.loc[:,'Ave'])**2).sum())/df.shape[0]
            results['variance'].append(var)
        min_index = numpy.argmin(results['variance'])
        for pn in param_names:
            param_ranges[pn][0] = results[pn][min_index] - param_units[pn]
            param_ranges[pn][1] = results[pn][min_index] + param_units[pn]
            param_ranges[pn][0] = max(param_ranges[pn][0], param_min)
            param_ranges[pn][1] = min(param_ranges[pn][1], param_max)
        if verbose:
            print('Optimization round {0}: params={1}'.format(i,current_params))
    out = dict()
    for k in results.keys():
        out[k] = results[k][min_index]
    return out

def get_month_params(df, param_min=0, param_max=10, max_step=1000, small_dif=10**-6,
                     method='DH2006', num_grid=3, window_size=0, verbose=False):
    assert window_size>=0, 'month_window should be positive value.'
    mparams = dict()
    for month in df.Month.dropna().unique():
        month = int(month)
        month_window = numpy.arange(month-window_size, month+window_size+1, 1)
        month_window = [ m if m>0 else m+12 for m in month_window ]
        is_month = (df['Month'].isin(month_window))
        mparams[str(month)] = get_params(df.loc[is_month,:],param_min,param_max,max_step,small_dif,
                                         method,num_grid,verbose)
        if verbose:
            print('Month', month_window, mparams[str(month)])
    return mparams

def get_photoperiod(start_date, end_date, lat, lon, timezone=0, elevation=3):
    dates = []
    sunrise = []
    sunset = []
    place = ephem.Observer()
    place.lon  = str(lon)
    place.lat  = str(lat)
    place.elev = elevation
    sun = ephem.Sun(place)
    dates = pandas.date_range(start_date, end_date)
    timezone_dates = [ d - datetime.timedelta(hours=timezone) for d in dates ]
    sunrise = [ ephem.localtime(place.next_rising(sun, start=x))  for x in timezone_dates ]
    sunset = [ ephem.localtime(place.next_setting(sun, start=x)) for x in timezone_dates ]
    sunrise = [ x + datetime.timedelta(hours=timezone) for x in sunrise ]
    sunset = [ x + datetime.timedelta(hours=timezone) for x in sunset ]
    photoperiod = [ (sunset - sunrise).seconds/3600 for sunset,sunrise in zip(sunset,sunrise) ]
    photoperiod2 = list()
    flag=0
    for i in range(len(photoperiod)): # correct the effect of daylight-saving time
        if i==0:
            photoperiod2.append(photoperiod[i])
        else:
            if i-flag>1:
                if (photoperiod[i]-photoperiod[i-1]>0.5):
                    photoperiod2.append(photoperiod[i]-1)
                    flag = i
                elif (photoperiod[i]-photoperiod[i-1]<-0.5):
                    photoperiod2.append(photoperiod[i]+1)
                    flag = i
                else:
                    photoperiod2.append(photoperiod[i])
            else:
                photoperiod2.append(photoperiod[i])
    df_pp = pandas.DataFrame({'Daytime':photoperiod2})
    df_pp['Year'] = dates.year
    df_pp['Month'] = dates.month
    df_pp['Day'] = dates.day
    df_pp['Sunrise'] = sunrise
    df_pp['Sunset'] = sunset
    df_pp['Sunrise_nondimensional'] = [ (x - x.normalize()).seconds/3600 for x in df_pp['Sunrise'] ]
    df_pp['Sunset_nondimensional'] = [ (x - x.normalize()).seconds/3600 for x in df_pp['Sunset'] ]
    return df_pp

