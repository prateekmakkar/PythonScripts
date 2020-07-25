import os
import requests
from bs4 import BeautifulSoup

# created by Prateek makkar
# https://trinket.io/python3/eb9fc9c57a?outputOnly=true&runOption=run
BOLD_END = '\033[0m'
BOLD_START = '\033[1m'

SERIES = "T.V Series"
MOVIES = "Movies"

genresList = ["Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary",
              "Drama", "Family", "Fantasy", "Game-Show", "History", "Horror", "Music", "Musical",
              "Mystery", "News", "Reality-TV", "Romance", "Sci-Fi", "Short", "Sport", "Talk-Show",
              "Thriller", "War"]
dictOfLinks = {}


def findTopRatedByFilters():
    genre = getInput(str, "Enter the genre from this list \n" +
                     "\n".join([",".join(genresList[i:i + 10]) for i in range(0, len(genresList), 10)]) +
                     ' (Press Enter for all genres)', "",
                     lambda x: len(x) == 0 or x.lower() in {i.lower() for i in genresList})
    printHashes()

    url = "https://www.imdb.com/search/title/?sort=user_rating&view=simple&num_votes=25000,"
    url += "&title_type=tv_series,mini_series" if dramaName == SERIES else "&title_type=feature"
    url += "&genres=" + genre

    print('Finding top ' + str(limit) + ' ' + str(dramaName) + ' from ' + (genre if genre != "" else "all") + ' genre'
        ' sorted desc by their user ratings with min 25000 votes: \n')
    source = requests.get(url)
    soup = BeautifulSoup(source.content, 'html5lib')
    a = 1
    for containerTag in soup.select('div[class="lister-item-content"]'):
        if a >= limit + 1:
            break

        nameTag = containerTag.select('div[class="col-title"] > span[class="lister-item-header"]'
                                      ' > span > a[href^="/title/tt"]')
        name = nameTag[0].text if len(nameTag) == 1 else ""

        dictOfLinks[a] = nameTag[0].attrs["href"]

        ratingTag = containerTag.select('div[class="col-imdb-rating"]')
        rating = ratingTag[0].text.replace("\n", "").strip() if len(ratingTag) == 1 else ""

        print(str(a) + '. ' + name + ' -> Rating: ' + str(rating))
        a += 1


def findTopRated():
    url = "https://www.imdb.com/chart/top/?ref_=nv_mv_250" if dramaName == MOVIES \
        else "https://www.imdb.com/chart/toptv/?ref_=nv_tvv_250"
    print('Finding top ' + str(limit) + ' ' + str(dramaName) + ' from chart \n')
    source = requests.get(url)
    soup = BeautifulSoup(source.content, 'html5lib')
    a = 1
    for containerTag in soup.select('tbody[class="lister-list"] > tr'):
        if a >= limit + 1:
            break
        for link in containerTag.select('td[class="titleColumn"] > a[href^="/title/tt"]'):
            name = link.text
            dictOfLinks[a] = link.attrs["href"]
        for ratingLink in containerTag.select('td[class="ratingColumn imdbRating"]'):
            rating = ratingLink.text.replace("\n", "").strip()

        print(str(a) + '. ' + name + ' with rating ' + str(rating))
        a += 1


def getContent(soup, regex):
    content = soup.select(regex)
    if len(content) > 0:
        return content[0].text.replace("\n", "").strip(), True
    else:
        return "", False


def getDetailsForSpecificDrama():
    link = dictOfLinks[detailForN]
    source = requests.get("https://www.imdb.com/" + link)
    soup = BeautifulSoup(source.content, 'html5lib')

    title, isSuccess = getContent(soup, 'div[class="title_wrapper"] > h1[class=""]')
    releaseDate, isSuccess = getContent(soup, 'div[class="title_wrapper"] > div[class="subtext"] > a[href^="/title/tt"]')
    duration, isSuccess = getContent(soup, 'div[class="title_wrapper"] > div[class="subtext"] > time')
    plotSummary, isSuccess = getContent(soup, 'div[class="summary_text"]')
    similarItemsList = []

    if not isSuccess:
        return

    for similarItemsTag in ((soup.select('div[class="rec_page"]')[0]).select('div[class="rec_item"]')):
        content = similarItemsTag.select('img[alt]')
        if len(content) > 0:
            similarItemsList.append(content[0].attrs["title"])

    print(BOLD_START + dramaName.upper() + BOLD_END + ": " + title)
    print(BOLD_START + "RELEASED: " + BOLD_END + releaseDate + BOLD_START + " | DURATION: " + BOLD_END + duration)
    print(BOLD_START + "PLOT SUMMARY: " + BOLD_END + plotSummary)
    print(BOLD_START + "MORE " + dramaName.upper() + " LIKE THIS : " + BOLD_END +
          ", ".join([similarItemsList[i] for i in range(0, len(similarItemsList))]))


def getInput(inputType, text, defaultValue, ConditionFilter):
    try:
        while True:
            userInput = int(input(text)) if inputType == int else str(input(text)).lower()
            if ConditionFilter(userInput):
                break
            print("You have chosen an Invalid option. Please choose the correct option")
    except ValueError:
        if defaultValue == -1:
            print("\nExiting....")
        else:
            print("Invalid Input provided. Proceeding with using default value as " +
                  BOLD_START + str(defaultValue) + BOLD_END)
        return defaultValue
    return userInput


def printHashes():
    print("#" * 150)


try:
    os.system("clear")
    printHashes()
    dramaType = getInput(int, "Enter '1' for TV Series & '2' for Movies ", MOVIES, lambda x: x < 3)
    limit = getInput(int, "Enter the number of top items (Max 250) you want ", 10, lambda x: x <= 250)

    dramaName = ("%s" % MOVIES) if dramaType == 2 else ("%s" % SERIES)
    printHashes()
    findTopRatedByFilters()
    # findTopRated()

    detailForN = getInput(int, "Enter the " + dramaName + " number for which you want to know the details."
                                                          " (Press Enter to exit)", -1, lambda x: x <= limit)
    printHashes()
    if detailForN != -1:
        getDetailsForSpecificDrama()

except:
    os.system('clear')
    print('OH SNAP ! SOMETHING WENT WRONG...')
