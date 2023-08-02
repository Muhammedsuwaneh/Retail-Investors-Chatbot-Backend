import openai
import pandas as pd
import os
import glob
import openai
import json

openai.api_key = "add open ai key here"

class ChatBot:

    def __int__(self):
        self.csv_data = {}

    def __filter_query(self, query):
        prompt = f"Extract the following from the query: 'year, company, subject'. Subject can be Total Revenue, Net Income / (Loss) Attributable to Common Shareholders, " \
                 f"Price to Earnings (P/E), Dividend Yield, Return on Equity (ROE).)\nquery: {query}"
        try:
            query_response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150
            )
        except:
            print("oops something went wrong:\n")
        else:
            response = query_response["choices"][0]['text'].strip()
            responseArr = response.split(":") # expected to return as "year: 2021 company: walmart subject: Total Revenue"
            year = responseArr[1].split()[0]
            company = responseArr[2].split()[0]
            subject = responseArr[3].strip()
            return year, company, subject

    def __load_csvdata(self):
        csv_files = glob.glob(os.path.join("../data", "*.csv"))
        dataframe = [pd.read_csv(csv_file) for csv_file in csv_files]
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
        # filter query
        fiscal_year, company, subject = self.__filter_query(self, query)
        company = company.capitalize() + " Inc"
        # load datasets
        self.__load_csvdata(self)

        # filter company data based on the filtered query
        filtered_data = self.__preprocess_datasets(self, company, int(fiscal_year))
        # send query request
        prompt = f"Using the dataset below \n{filtered_data}\n\nAnswer the question\n: {query}\nPay attention to the subject: {subject}"
        openai_response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150
        )
        # get response
        response = openai_response['choices'][0]['text'].strip()
        return response


def main():
    chatbot_object = ChatBot()
    query = input("Question: ")
    answer = chatbot_object.answer_question(query)
    print(f"Answer: {answer}")


if __name__ == '__main__':
    main()