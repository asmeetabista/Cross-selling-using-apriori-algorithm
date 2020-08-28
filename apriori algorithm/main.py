"""
Created by: Asmita Bista
Created on: 07/18/2020
"""

import itertools
import pandas as pd
import xlrd


class CrossSelling():
    def __init__(self):
        """
        INPUT_DATA = input file consisting transaction data
        MIN_SUPPORT is the minimum frequency of item in the dataset group by transaction date
        max_items = maximum number of items in a transaction
        """
        self.INPUT_DATA = 'grocery_sampledata.xlsx'
        self.MIN_SUPPORT = 2
        self.records = []
        self.max_items = 10
        pass

    def prepare_data(self):
        """
        Takes input and converts the items into list
        :return: sorted list of items
        """
        input_dataset = pd.read_excel(self.INPUT_DATA)
        # removing transaction_date and quantity because they are same for all records
        df = input_dataset[['transaction_id', 'items']]

        df = df.groupby('transaction_id')['items'].apply(','.join).reset_index()

        df = df.drop(columns={'transaction_id'})
        input_dataset = df['items'].str.split(',', self.max_items, expand=True)

        items_count = len(input_dataset)
        max_items_count = len(input_dataset.columns)

        # converting the items into list
        for i in range(0, items_count):
            self.records.append([str(input_dataset.values[i, j]) for j in range(0, max_items_count)])

        # Putting all the records in same line
        items = sorted([item for sublist in self.records for item in sublist if item != 'None'])
        return items

    def check_subset(self, key_items, list_items, flag):
        """
        check whether input key_items are subset of the list_items
        :param key_items: first list
        :param list_items: second list
        :param flag: flag to determine the number of combinations
        :return: true or false depending on whether key_items is subset of list_items
        """
        if flag == 0:
            return set(key_items) <= set(list_items)
        else:
            if flag > 1:
                key_subsets = list(itertools.combinations(key_items, flag))
            else:
                key_subsets = key_items
            for i in key_subsets:
                if i not in list_items:
                    return False
            return True

    def calculate_count(self, listed_items):
        """
        :param listed_items: sorted list of all items
        :return: dictionary containing the count of each item
        """
        items_count_dict = {i: listed_items.count(i) for i in listed_items}
        items_count = {}
        # List of all items having count >= minimum support
        for key, value in items_count_dict.items():
            if value >= self.MIN_SUPPORT:
                items_count[key] = value
        return items_count

    def calculate_combined_items_count(self, input_items_count, num_combination):
        """
        :param input_items_count: dictionary containing the count of each item
        :param num_combination: number of combination of items of item_count
        :return: dictionary containing the count of each combination of items
        """
        if num_combination == 1:
            input_items_count = sorted(list(input_items_count.keys()))
            # just creating all possible combinations of items_count
            sorted_items_count = list(itertools.combinations(input_items_count, 2))
        else:
            input_items_count = list(input_items_count.keys())
            sorted_items_count = sorted(list(set([item for t in input_items_count for item in t])))
            sorted_items_count = list(itertools.combinations(sorted_items_count, num_combination + 1))

        output_items_count_dict = {}
        output_items_count = {}

        for i in sorted_items_count:
            count = 0
            for j in self.records:
                # if contents of i is subset of j is true
                if self.check_subset(i, j, 0):
                    count += 1
            output_items_count_dict[i] = count
        for key, value in output_items_count_dict.items():
            if value >= self.MIN_SUPPORT:
                if self.check_subset(key, input_items_count, num_combination):
                    output_items_count[key] = value
        return output_items_count

    def find_item_support_count(self, item_key, item_list):
        """
        :param item_key: item set
        :param item_list: dictionary of all combinations of items_count
        :return: support count of item set
        """
        return item_list[item_key]

    def calculate_confidence(self, item_list1, item_list2, item_list3, item_list4):
        """
        :param item_list1: items with single combination
        :param item_list2: list of items with two combinations and their count
        :param item_list3: list of items with three combinations and their count
        :param item_list4: list of items with four combinations and their count
        :return: confidence of associated items
        """
        # merging all the items and their count in one dictionary
        items_list_dict = {**item_list1, **item_list2, **item_list3, **item_list4}

        items_list = []
        for i in list(item_list3.keys()):
            subsets = list(itertools.combinations(i, 2))
            items_list.append(subsets)
            items_list3_key = list(item_list3.keys())

        for i in range(0, len(items_list3_key)):
            for j in items_list[i]:
                items_together = j
                items_together = ' and '.join(items_together)
                recommend_item = set(items_list3_key[i]) - set(j)
                recommend_item = ''.join(recommend_item)
                confidence = (self.find_item_support_count(items_list3_key[i], items_list_dict) / self.find_item_support_count(j, items_list_dict)) * 100
                print("The chances of buying {} while buying {} together is ".format(recommend_item, items_together), confidence)


obj = CrossSelling()
items = obj.prepare_data()
items_count = obj.calculate_count(items)
items_count_2 = obj.calculate_combined_items_count(items_count, 1)
items_count_3 = obj.calculate_combined_items_count(items_count_2, 2)
items_count_4 = obj.calculate_combined_items_count(items_count_3, 3)
obj.calculate_confidence(items_count, items_count_2, items_count_3, items_count_4)









