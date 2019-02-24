import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def clean(dataframe):
    for i in dataframe:
        i.replace(' ','')
    # new_date = dataframe['Date of Publication'].str.extract(r'^(\d{4})', expand=False)
    # new_date = pd.to_numeric(new_date)
    # new_date = new_date.fillna(0)
    # dataframe['Date of Publication'] = new_date

    return dataframe

def obtain_data():
    df = pd.read_csv('Olympics_dataset1.csv', index_col=0, skiprows=1)
    df.head(5)

def print_dataframe(dataframe, print_column=True, print_rows=True):
    # print column names
    if print_column:
        print(",".join([column for column in dataframe]))
    # print rows one by one
    if print_rows:
        for index, row in dataframe.iterrows():
            print(",".join([str(row[column]) for column in dataframe]))

def question_1():
    csv_file1 = 'Olympics_dataset1.csv'
    csv_file2 = 'Olympics_dataset2.csv'

    #read file
    df1 = pd.read_csv(csv_file1, skiprows=1, thousands=',')
    df2 = pd.read_csv(csv_file2, skiprows=1, thousands=',')

    # merge the two dataframes
    # df_merge = pd.merge(df1, df2, how='left', left_on=['Team'], right_on=['Team'])
    df = pd.merge(df1, df2, on='Unnamed: 0')

    # # Group by Country and keep the country as a column
    # gb_df = df.groupby(['Country'], as_index=False)
    #
    # # Select a column (as far as it has values for all rows, you can select any column)
    # df = gb_df['Identifier'].count()
    df.rename(columns={'Unnamed: 0': 'Country'}, inplace=True)

    df.apply(pd.to_numeric, errors='ignore')

    df.astype(int, errors='ignore')
    clean(df)
    # print the dataframe which shows publication number by country
    return df

def question_2():
    df = question_1()
    df = df.set_index(['Country'])
    return df

def question_3():
    df = question_1()
    df = df.drop(columns=['Rubish'])
    return df

def question_4():
    df = question_1()
    df = df.dropna(how='any')
    return df

def question_5():
    df = question_4()
    df = df.drop(df.index[-1])
    index = df['Gold_x'].idxmax()
    country_rec = df.loc[index]
    return country_rec

def question_6():
    df = question_4()
    df = df.drop(df.index[-1])
    df['Gold_Different'] = abs(df.Gold_x - df.Gold_y)
    index = df['Gold_Different'].idxmax()
    country_rec = df.loc[index]
    return country_rec

def question_7():
    df = question_4()
    df = df.drop(df.index[-1])
    df = df.sort_values('Total.1', ascending=False)
    return df

def question_8():
    df = question_7()
    df = df.head(10)
    df = df[['Country','Total_x','Total_y']]
    # print_dataframe(df)
    # df = df.groupby(['Country','Total_x'])['Country'].count().unstack('Total_y').fillna(0)
    # df.plot(kind='barh', stacked=True)
    df = df.groupby('Country').sum().plot(kind='barh', stacked=True, title="Medals for Winter and Summer Games")
    # df.set_xlabel("Customers")
    # df.set_ylabel("Sales")
    # df = df.groupby('Country').sum().unstack()
    # df.plot.bar(kind='barh', stacked=True)
    df.legend(['Summer Games', 'Winter Games'])
    plt.tight_layout()
    plt.show()

def question_9():
    df = question_1()
    # df = df.head(10)
    df = df[['Country', 'Gold_y', 'Silver_y','Bronze_y']]
    df = df.iloc[[143,6,52,70,97]]
    # print(df)
    # print_dataframe(df)
    # df = df.groupby(['Country','Total_x'])['Country'].count().unstack('Total_y').fillna(0)
    # df.plot(kind='barh', stacked=True)
    # df = df.groupby('Country').sum().plot(kind='barh', stacked=True, title="Medals for Winter and Summer Games")
    df = df.groupby('Country').sum().fillna(0)
    # df.plot.bar(kind='barh', stacked=True)
    df = df.plot(kind='bar',title="Winter Games")
    df.legend(['Gold', 'Silver', 'Bronze'],loc=9,ncol=4)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Result for question1:\n")
    df = question_1()
    # print(df.head(5))
    print_dataframe(df.head(5))
    print('\n')

    print("Result for question2:\n")
    df = question_2()
    print(df.index[0],'\n')
    # print_dataframe(df.head(5))

    print("Result for question3:\n")
    df = question_3()
    print_dataframe(df.head(5))
    print('\n')

    print("Result for question4:\n")
    # df = question_1()
    # print_dataframe(df.tail(10))
    # print('\n')
    question_4()
    # print(df.tail(10))
    print_dataframe(df.tail(10))
    print('\n')

    print("Result for question5:\n")
    df = question_5()
    print(df)
    print('\n')

    print("Result for question6:\n")
    df = question_6()
    print(df)
    print('\n')

    print("Result for question7:\n")
    df = question_7()
    new_df = df.head(5)
    new_df = new_df.append(df.tail(5))
    print_dataframe(new_df)
    print('\n')

    print("Result for question8:\n")
    question_8()
    # print_dataframe(df)
    # print('\n')

    print("Result for question9:\n")
    question_9()


