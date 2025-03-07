#!/usr/bin/env python
# coding: utf-8

# In[1]:


# plotly standard imports
import plotly.graph_objs as go
import chart_studio.plotly as py

# Cufflinks wrapper on plotly
import cufflinks

# Data science imports
import pandas as pd
import numpy as np

# Options for pandas
pd.options.display.max_columns = 30

# Display all cell outputs
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'

from plotly.offline import iplot, init_notebook_mode
cufflinks.go_offline(connected=True)
init_notebook_mode(connected=True)

# Set global theme
cufflinks.set_config_file(world_readable=True, theme='pearl')


# # Load dataset
# And get interesting features

# In[2]:


from src.load_datasets import load_datasets
from src.prepare_datasets import feature_list

train, test = load_datasets()

train_features = train[feature_list]
test_features = test[feature_list]

train_features.index = pd.to_datetime(train.pop('timestamp'), unit='ms')
test_features.index = pd.to_datetime(test.pop('timestamp'), unit='ms')

train_features


# # Data featuring
# 
# In theory we are going to use 4 features: The price itself and three extra technical indicators.
# 
# MACD (Trend)
# Stochastics (Momentum)
# Average True Range (Volume)
# 
# ## Functions
# 
# **Exponential Moving Average**: Is a type of infinite impulse response filter that applies weighting factors which decrease exponentially. The weighting for each older datum decreases exponentially, never reaching zero.
# 
# **MACD**: The Moving Average Convergence/Divergence oscillator (MACD) is one of the simplest and most effective momentum indicators available. The MACD turns two trend-following indicators, moving averages, into a momentum oscillator by subtracting the longer moving average from the shorter moving average.
# 
# **Stochastics oscillator**: The Stochastic Oscillator is a momentum indicator that shows the location of the close relative to the high-low range over a set number of periods.
# 
# **Average True Range**: Is an indicator to measure the volalitility (NOT price direction). The largest of:
# 
# - Method A: Current High less the current Low
# - Method B: Current High less the previous Close (absolute value)
# - Method C: Current Low less the previous Close (absolute value)

# In[3]:


from ta import add_all_ta_features
from ta.utils import dropna 

days_to_show = 60
items_to_show = days_to_show * 24 * 60

# Dropna from ta also remove zeros and max double value
df_show = dropna(train_features[-items_to_show:])

df_show = add_all_ta_features(
    df_show, 
    open="open", 
    high="high", 
    low="low", 
    close="close", 
    volume="volume", 
    fillna=True
)
df_show = df_show[[
         'open', 'high', 'low', 'close', 'volume',
         'volatility_bbm', 'volatility_bbh', 'volatility_bbl',
         'trend_macd', 'momentum_rsi', 'volatility_kchi',
         'trend_ichimoku_conv', 'trend_ichimoku_a', 'trend_ichimoku_b',
         'momentum_stoch', 'momentum_stoch_signal', 'volatility_atr'
]]


# ## MACD

# In[4]:



df_show[['trend_macd', 'close']].iplot(subplots=True)


# ## Stochastics Oscillator

# In[5]:


df_show[['momentum_stoch','momentum_stoch_signal', 'close']].iplot(subplots=True)


# ## Average True Range

# In[6]:


df_show[['volatility_atr', 'close']].iplot(subplots=True)


# ## Check for normal distribution

# In[7]:


import scipy.stats as stats
import pylab

close_change = train_features['close'].pct_change()[1:]
close_change.head()

stats.probplot(close_change, dist='norm', plot=pylab)


# ### Check time relation
# 
# Check depenence of trading and price from date in year and time of day
# 
# #### Firstly define function for display frequiency

# In[4]:


import tensorflow as tf
import matplotlib.pyplot as plt

def plot_log_freaquency(series):
    fft = tf.signal.rfft(series)    
    f_per_dataset = np.arange(0, len(fft))

    n_samples_d = len(series)
    days_per_year = 365
    years_per_dataset = n_samples_d/(days_per_year)

    f_per_year = f_per_dataset/years_per_dataset
    plt.step(f_per_year, np.abs(fft))
    plt.xscale('log')
    plt.xticks([1, 365], labels=['1/Year', '1/day'])
    _ = plt.xlabel('Frequency (log scale)')


# ### Frequency of price

# In[9]:


plot_log_freaquency(train_features['close'])


# ### Frequence of price change

# In[ ]:


plot_log_freaquency(train_features['close'].diff().dropna())


# ### Frequency of transaction volume

# In[ ]:


plot_log_freaquency(train_features['volume'])


# ### Frequence of transaction volume change 

# In[1]:


plot_log_freaquency(train_features['volume'].diff().dropna())


# ## Compare train and test datasets

# In[ ]:


import sweetviz as sv

compare_report = sv.compare([train_features, 'Train data'], [test_features, 'Test data'], "close")
compare_report.show_notebook()


# ### Training data exploration

# In[3]:


train_features[59::60].iplot(subplots=True)


# ### Testing data exploration

# In[4]:


test_features[59::60].iplot(subplots=True)


# ## Normalise data
# 
# Will use only training mean and deviation for not give NN access to test dataset
#  
# Divide by the max-min deviation
# 

# In[5]:


pd.set_option('float_format', '{:.2f}'.format)

train_features.describe()


# In[6]:


test_features.describe()


# maximum for training to litle, and not will allow correctly predict values in testing dataset,
# will use manually choosed value for maximum
# 100 thouthands dollars
# except of volume

# In[13]:


from sklearn.preprocessing import MinMaxScaler
import numpy as np

train_min = np.min(train_features)
train_max = np.max(train_features)

MAX_TARGET = 100000

train_max['high'] = MAX_TARGET
train_max['low'] = MAX_TARGET
train_max['open'] = MAX_TARGET
train_max['close'] = MAX_TARGET

train_fit = pd.DataFrame([train_min, train_max])

scaler = MinMaxScaler()
scaler = scaler.fit(train_fit)


# In[18]:


print("normalise train dataset...")
train_normalised = pd.DataFrame(scaler.transform(train_features))
train_normalised.columns = train_features.columns
train_normalised.index = train_features.index

print("normalise test dataset...")
test_normalised = pd.DataFrame(scaler.transform(test_features))
test_normalised.columns = test_features.columns
test_normalised.index = test_features.index

train_normalised.head()


# In[19]:


train_normalised[59::60].iplot(subplots=True, title="Train")

test_normalised[59::60].iplot(subplots=True, title="Test")


# In[20]:


train_in_hours = train_features[59::60]

feature2normaliesd = pd.DataFrame({ 
    'Real': train_in_hours['close'], 
    'Normalised': train_normalised['close'][59::60]
})
feature2normaliesd.index = train_in_hours.index

feature2normaliesd.iplot(subplots=True)


# In[ ]:





# In[ ]:




