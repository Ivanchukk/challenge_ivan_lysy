import requests
import json
import time
import datetime
import math

# request data by block number
def get_data(block_height):
    r = requests.get(f'https://blockchain.info/block-height/{block_height}?format=json')
    html = r.text
    res = json.loads(html)
    return res


# get the timestamp from the requested block
def get_timestamp(block):
    return block['blocks'][0]['time']


# This is helpper to see the unix in datetime format
def unix_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


# Here will be most of the calculation
# THe algo splitting the range of blocks (Example Block 500 to 10000) and deciding what to do next.
# It always looking for two date and checking if the requested data by the user in the range.
# b1 the left side of the range, b2 the right side, latest_block is a most resent block
class Calculator:
    def __init__(self, b1, b2, latest_block):
        self.b1 = b1
        self.b2 = b2
        self.latest_block = latest_block

    def get_range(self):
        b1_id = get_data(self.b1)
        if self.b2 > self.latest_block:
            self.b2 = self.latest_block
        b2_id = get_data(self.b2)
        self.t1 = get_timestamp(b1_id)
        self.t2 = get_timestamp(b2_id)

        return self.t1, self.t2

    def new_edges(self, wanted_time):
        if self.t1 < wanted_time < self.t2:
            # I made all of this if's to get closer to the correct answer.
            # If I am using only: math.floor((self.b1 + self.b2)/2) it will jump between the ranges.
            # This part have to be done better as it not work properly with large numbers (Block 700K+)
            if self.b2 - self.b1 == 1:
                return self.b1, self.b2
            elif self.b2 - self.b1 <= 3:
                self.b1 = math.floor(self.b1+1)
                self.b2 = math.floor(self.b2)
            elif self.b2 - self.b1 < 10:
                self.b1 = math.floor(self.b1+1)
                self.b2 = math.floor(self.b2-1)
            else:
                self.b1 = math.floor((self.b1 + self.b2)/2)
                self.b2 = math.floor(self.b2)
        elif wanted_time > self.t2:
            self.b1 = int(self.b2)
            self.b2 = int(self.b2 * 1.1)

        elif wanted_time < self.t1:
            self.b2 = int(self.b1)
            self.b1 = int(self.b1 * 0.25)

        return self.b1, self.b2

    def run_class(self, needed_time_stamp):
        self.t1, self.t2 = self.get_range()
        self.b1, self.b2 = self.new_edges(needed_time_stamp)
        return self.b1, self.b2, self.t1, self.t2


# This is the first runner and Checker of the results
def runner(needed_time_stamp, latest_block):
    # The initial split of the blocks 0----b1--------b2----latest_block
    b1 = int(latest_block*0.33)
    b2 = int(latest_block*0.66)

    ca = Calculator(b1, b2, latest_block)

    while True:
        bb1, bb2, tFinal1, tFinal2 = ca.run_class(needed_time_stamp)
        if abs(bb1 - bb2) == 1:
            break

    if tFinal1 < needed_time_stamp < tFinal2:
        final_res = bb1
    elif tFinal2 > needed_time_stamp:
        final_res = bb1
    else:
        final_res = bb2
    return final_res


# This function responsible on client request. What timestamp he's looking for.
def client_input():
    theBlock = 762448 # This is the latest block inthe time of doing. I gave an option to replace it by input.
    needed_time_stamp = input("To find the block you looking for enter unix timestamp: ")
    latest_block = input(f"Please enter latest block number."
                         f"\nIf you dont want to the program will"
                         f" not find blocks > {theBlock}."
                         f"\nYou can just press enter if you dont want to insert block number.")
    try:
        if latest_block == "":
            latest_block = theBlock
        elif latest_block < int(theBlock):
            latest_block = theBlock
        else:
            latest_block = int(theBlock)
    except:
        latest_block = theBlock

    if needed_time_stamp[0].lower() == "r":
        needed_time_stamp = int(needed_time_stamp[1:])
    else:
        needed_time_stamp = int(needed_time_stamp)
    return needed_time_stamp, latest_block
# Press the green button in the gutter to run the script.


if __name__ == '__main__':
    needed_time_stamp, latest_block = client_input()
    final_res = runner(needed_time_stamp, latest_block)
    print(f"You looking for block: {final_res}")
    print("link:")
    print(f"https://blockchain.info/block-height/{final_res}?format=json")





