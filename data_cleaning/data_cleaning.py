import pandas as pd
import numpy as np

df = pd.read_csv('./data/un-country-data.csv')
countries = df[df['ISO3_code'].notnull()]

columns = ['ISO3_code', 
           'Location',
           'Time',
           'TPopulation1Jan',
           'TPopulation1July']

clean_df = countries[columns]

clean_df.to_csv('./data/clean-data.csv', index=False)

pop_data = pd.read_csv('./data/clean-data.csv')

pop_data.rename(columns={'Location': 'label',
                         'Time': 'dt',
                            'TPopulation1July': 'x'}, inplace=True)
pop_data.drop(columns=['TPopulation1Jan', 'ISO3_code'], inplace=True)

pop_data.to_csv('./data/clean-formatted-data.csv', index=False)


#Getting all top10 countries in the time-gap given
years = np.arange(1950,2101).tolist()
top_countries_per_year = []
for year in years:
    top_10_year = pop_data[pop_data['Time'] == year].nlargest(10, 'TPopulation1Jan')['Location'].tolist()
    for i in top_10_year:
        if i not in top_countries_per_year:
            top_countries_per_year.append(i)
print(top_countries_per_year)