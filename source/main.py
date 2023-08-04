import openai
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os
import glob
import openai
import json

class ChatBot:

    def __int__(self):
        self.csv_data = {}
        self.companies = []

    def __get_companies(self):
        self.companies = set(self.csv_data[0]["name"])

    def __filter_query(self, query):
        prompt = f"Extract the following from the query: 'year, company, subject'. Subject can be Total Revenue, Net Income / (Loss) Attributable to Common Shareholders, " \
                 f"Price to Earnings (P/E), Dividend Yield, Return on Equity (ROE).). company must be from this list: {self.companies}\nquery: {query}\nreturn response in JSON format"
        try:
            query_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{ "role": "user", "content": prompt }],
            max_tokens=100
            )
        except Exception as ex:
            print(f"oops something went wrong: {ex}\n")
        else:
            response = query_response['choices'][0]['message']['content']
            json_object = json.loads(response) # { year: value, company: value, subject: value }
            return json_object['year'], json_object['company'], json_object['subject']

    def __load_csvdata(self):
        try:
            csv_files = glob.glob(os.path.join("../data", "*.csv"))
            dataframe = [pd.read_csv(csv_file) for csv_file in csv_files]
        except FileNotFoundError as fx:
            print(fx)
            exit(-1)
        except PermissionError as pr:
            print(pr)
            exit(-1)
        else:
            self.csv_data = dataframe

    def __preprocess_datasets(self, company, fiscal_year):

        filtered_data_1 = self.csv_data[0][(self.csv_data[0]["name"] == company) & (self.csv_data[0]["fiscal_year"] == fiscal_year)]
        filtered_data_2 = self.csv_data[2][(self.csv_data[2]["name"] == company) & (self.csv_data[2]["fiscal_year"] == fiscal_year)]
        filtered_data_3 = self.csv_data[4][(self.csv_data[4]["name"] == company) & (self.csv_data[4]["fiscal_year"] == fiscal_year)]
        filtered_data_4 = self.csv_data[6][(self.csv_data[6]["name"] == company) & (self.csv_data[6]["fiscal_year"] == fiscal_year)]

        combined_filtered_data = pd.concat([filtered_data_1, filtered_data_2, filtered_data_3, filtered_data_4], axis=0)
        return combined_filtered_data

    @classmethod
    def answer_question(self, query: str) -> str:
        # get api secret key
        try:
            load_dotenv(find_dotenv())
            openai.api_key = os.environ.get('OPENAI_API_KEY')
        except Exception as ex:
            print(ex)
            exit(-1)

        # load datasets
        self.__load_csvdata(self)

        # get all companies
        self.__get_companies(self)

        # filter query
        fiscal_year, company, subject = self.__filter_query(self, query)

        # filter company data based on the filtered query
        filtered_data = self.__preprocess_datasets(self, company, int(fiscal_year))

        # send query request
        try:
            prompt = f"Only use the dataset below as a source of reference\n" \
                     f"dataset\n{filtered_data}\n\nAnswer the question\n: {query}\nPay attention to the subject: {subject}"
            query_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
        except Exception as ex:
            print(ex)
            exit(-1)
        else:
            response = query_response['choices'][0]['message']['content']
            return response


def main():
    chatbot_object = ChatBot()
    query = input("Question: ")
    answer = chatbot_object.answer_question(query)
    print(f"Answer: {answer}")


if __name__ == '__main__':
    main()