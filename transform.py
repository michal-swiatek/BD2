import cx_Oracle
import pandas as pd


def generate_buildings():
    pass

users_emails = pd.read_csv('mock_data/users_with_emails.csv')
users_phones = pd.read_csv('mock_data/users_with_phones.csv')

companies_emails = pd.read_csv('mock_data/companies_emails.csv')
companies_phones = pd.read_csv('mock_data/companies_phones.csv')

def merge(df_emails, df_phones, write_name):
    
    """
    Need to pass one entity divided on 2 parts - ones with phones and ones with emails
    """

    df_emails_no_id = df_emails
    df_phones_no_id = df_phones

    if 'id' in df_emails.columns:
        df_emails_no_id = df_emails.drop('id', axis=1)

    if 'id' in df_phones.columns:
        df_phones_no_id = df_phones.drop('id', axis=1)

    

    df_emails_no_id['phone'] = [None for _ in range(len(df_emails_no_id))]
    df_phones_no_id['email'] = [None for _ in range(len(df_phones_no_id))]

    result_df = pd.concat([df_emails_no_id, df_phones_no_id], axis=0)
    result_df.to_csv(write_name, index=False)
    
    print("Merged:3")

merge(users_emails, users_phones, 'data/users.csv')
merge(companies_emails, companies_phones, 'data/companies.csv')