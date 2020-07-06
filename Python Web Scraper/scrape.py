#imports
import urllib.request
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
from collections import Counter

def getUrlText():
    connected = False

    response = None

    while not connected:
        try:
            response = urllib.request.urlopen(input("Enter a URL: "))
        except ValueError:
            print("Invalid URL.")
        else:
            connected = True

    soup = BeautifulSoup(response.read(), "html.parser")

    pageText = ""

    for pTag in soup.find_all("p"):
        pageText += pTag.get_text()

    return pageText

print("Web Scraping Data Analysis Tool")

connected = False

pageText = getUrlText()

action = ""

while True:
    action = input("Would you like to view text (view), analyse text (analyse), choose a new URL (new), apply ReGex match removals (regex), or exit the program (quit)? ")    
    
    print()

    if action == "quit":
        # exit while loop
        break
    elif action == "view":
        # print out entire page text
        print(pageText)
        print()
    elif action == "new":
        # re-run scraper method
        pageText = getUrlText()
        print()
    elif action == "analyse":
        # perform analysis on given text
        print("What analysis should be performed on the text data?")
        print("Letter frequency analysis (freq-letter)")
        print("Word frequency analysis (freq-word)")
        print()
        choice = input("Choice: ")
        print()
        if choice == "freq-letter":
            data = Counter(pageText)
            print(data)
            letters = list(data.keys())
            values = list(data.values())
            fig, axs = plt.subplots(1, 1, figsize=(9, 9), sharey=True)
            axs[0].bar(letters, values)
            #axs[1].scatter(letters, values)
            #axs[2].plot(letters, values)
            fig.suptitle("Letter frequency")
            plt.show()
        elif choice == "freq-word":
            print(Counter(pageText.lower().translate(str.maketrans(dict.fromkeys(",.?/!()"))).split()))
        else:
            print("Invalid choice.")
        print()
    elif action == "regex":
        pageText = re.sub(input("What is the RegEx match removal you want to apply? "), "", pageText)
        print()
    else:
        print("Invalid choice.")
        
print("Thank you for using my Web Scraper Data Analysis Tool")
print("Created by Robert Dancer - RobCoder102 - robertdancer@ymail.com")