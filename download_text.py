# download_text.py
# author: Diego Magdaleno
# This program scrapes various works of fiction from sources such as Project Gutenburg,
# Open Library, Archive of our Own (Ao3), and Fan Fiction.net (FFnet). These texts are
# saved locally in a compressed format, but are uncompressed into txt files for
# training OpenAI's GPT-2 model.
# Python 3
# Windows/MacOS/Linux


import os
import time
import math
import json
import requests
from bs4 import BeautifulSoup as bsoup


class Gutenberg():
    def __init__(self):
        # Initialize some important variables, such as the list of valid fantasy
        # subjects available in Project Gutenberg, the mapping of each subject to
        # its respective bookshelf value, and the mapping of each subject to the
        # expected number of downloads available.
        self.valid_subjects = self.get_subjects()
        self.subject_to_bookshelf = self.get_subjects_to_bookshelf()


    # Send a request to the Project Gutenberg page regarding Fantasy and Fiction and
    # return the page as a beautifulsoup object.
    # @param: Takes no arguments.
    # @return: Returns a None if the request was unsuccessful. Otherwise, a beautifulsoup
    #   object of the response's html is returned.
    def get_fantasy_page(self):
        # URL to the Fantasy section of Project Gutenberg.
        fantasy_url = "https://www.gutenberg.org/ebooks/bookshelves/search/?query=fiction" +\
                        "|adventure|fantasy|humor|horror|western"

        # Send the request to that URL.
        response = requests.get(fantasy_url)

        # Get the return status code.
        if response.status_code != 200:
            print("Error: Recieved status code " + str(response.status_code) + " from " +\
                    fantasy_url)
            return None

        # Return the beautifulsoup object from the html.
        return bsoup(response.content, features="lxml")


    # Find a list of all available Fantasy subjects from Project Gutenberg.
    # @param: Takes no arguments.
    # @return: Returns a list of all available Fantasy subjects from Project Gutenberg.
    def get_subjects(self):
        # Initialize the return list.
        subjects_list = []

        # Pull the Fantasy page from Project Gutenburg. If None was returned, then
        # return the empty list.
        fantasy_soup = self.get_fantasy_page()
        if fantasy_soup == None:
            return subjects_list

        # Get all elements containing the names of subjects.
        link_tags = fantasy_soup.find_all("span", {"class": "title"})

        # Extract the text from each of those elements and append them to the list.
        for link in link_tags:
            if "Sort" not in link.text:
                subjects_list.append(link.text)

        # Return the list of available fantasy subjects.
        return subjects_list


    # Create a mapping of all subjects to their corresponding bookshelf.
    # @param: Takes no arguments.
    # @return: Returns a dictionary of all subjects to their corresponding bookshelf.
    def get_subjects_to_bookshelf(self):
        # Initialize the return dictionary.
        subjects_to_bookshelf = {}

        # Pull the Fantasy page from Project Gutenburg. If None was returned, then
        # return the empty dictionary.
        fantasy_soup = self.get_fantasy_page()
        if fantasy_soup == None:
            return subjects_to_bookshelf

        # Get all elements containing the URL extensions for a subject.
        link_tags = fantasy_soup.find_all("li", {"class": "navlink"})

        # Extract the URL extension and subsequently, the bookshelf number from each
        # of those elements and map them to their corresponding subject.
        valid_subjects_list = self.get_subjects()
        for link in link_tags:
            url_extension = link.find("a")["href"]
            bookshelf = url_extension.split("/")[-1]
            subject = link.find("a").find("span", {"class": "title"}).text
            if subject in valid_subjects_list:
                subjects_to_bookshelf[subject] = bookshelf

        # Return the dictionary mapping of subjects to their corresponding bookshelf.
        return subjects_to_bookshelf


    # Create a mapping of all subjects to their corresponding number of available
    # downloads.
    # @param: Takes no arguments.
    # @return: Returns a dictionary of all subjects to their corresponding number of
    #   available downloads.
    def get_subjects_to_downloads(self):
        # Initialize the return dictionary.
        subjects_to_downloads = {}

        # Pull the Fantasy page from Project Gutenburg. If None was returned, then
        # return the empty dictionary.
        fantasy_soup = self.get_fantasy_page()
        if fantasy_soup == None:
            return subjects_to_downloads

        # Get all elements containing the URL extensions for a subject.
        link_tags = fantasy_soup.find_all("li", {"class": "navlink"})

        # Extract the number of downloads and map them to their corresponding subject.
        valid_subjects_list = self.get_subjects()
        for link in link_tags:
            downloads = link.find("span", {"class": "title"}).text.replace(" downloads", "")
            subject = link.find("span", {"class": "title"}).text
            if subject in valid_subjects_list:
                subjects_to_downloads[subject] = int(downloads)

        # Return the dictionary mapping of subjects to their corresponding number of
        # downloads.
        return subjects_to_downloads


    # Download the specified text.
    # @param: link_extension, the URL extension to the text's download page.
    # @param: title, the title of the text.
    # @param: subject, a valid subject within the Fantasy section of Project Gutenberg.
    # @return: Returns nothing.
    def download_text_file(self, link_extension, title, subject):
        # Verify that the subject argument is valid.
        if subject not in self.valid_subjects:
            return

        # Build the URL to scrape from the text page.
        text_url = "https://www.gutenberg.org" + link_extension

        # Send a request to the page.
        page_response = requests.get(text_url)

        # Get the return status code.
        if page_response.status_code != 200:
            print("Error: Recieved status code " + str(page_response.status_code) + " from " +\
                    text_url)
            return

        # Get the beautifulsoup object from the html.
        page_soup = bsoup(page_response.content, features="lxml")

        # Get the table element from the page.
        sources_table = page_soup.find("table", {"class": "files"})

        # From the table element, extract the entries that have the URL extensions
        # for the different download sources. Iterate over the contents of each entry.
        entries = sources_table.find_all("td", {"property": "dcterms:format"})
        for entry in entries:
            # Extract the link for the download source.
            link = entry.find("a")["href"]

            # If the link for the download source ends with ".txt" or ".txt.utf-8",
            # Send a request to the download source and save the response (the text)
            # to a file.
            if link.endswith(".txt") or link.endswith(".txt.utf-8"):
                download_response = requests.get("https://www.gutenberg.org" + link)

                # Get the return status code.
                if download_response.status_code != 200:
                    print("Error: Recieved status code " + str(download_response.status_code) +\
                            " for downloading text " + title)
                    return

                # The content of the request should contain all of the text within
                # the title. Be sure to clean it up if necessary.
                download_content = bsoup(download_response.content, features="lxml").text
                download_content = download_content.replace("\r\n", "\n")

                # Some housekeeping in regards to files. Check for a Gutenberg directory
                # as well as a subdirectory in there for the subject. Make the respective
                # directories if they don't exist.
                if not os.path.exists("Gutenberg") or not os.path.isdir("Gutenberg"):
                    os.mkdir("Gutenberg")
                if not os.path.exists("./Gutenberg/" + subject):
                    os.mkdir("./Gutenberg/" + subject)

                # Some housekeeping in regards to the title. Certain characters are not
                # allowed in file names.
                title = title.replace("\r", "").replace("?", "").replace(":", "-")
                title = title.replace("*", "").replace("\"", "")
                
                # Create the file name. Open and write to the new file under that name.
                file_name = "./Gutenberg/" + subject + "/" + title + ".txt"
                file = open(file_name, "w+", encoding="utf-8")
                file.write(download_content)
                file.close()

                # Return the function.
                return
                      
        # Return the function.
        return


    # Download all available texts from a subject.
    # @param: subject, a valid subject within the Fantasy section of Project Gutenberg.
    # @param: limit, an integer value representing the maximum number of texts to be
    #   downloaded from the subject. Default value is 1000.
    # @return: Returns nothing.
    def download_from_subject(self, subject, limit=1000):
        # Verify that the subject argument is valid.
        if subject not in self.valid_subjects:
            return

        # Verify that the limit argument is valid (greater than 0).
        if limit < 1:
            return

        # This static variable represents the maximum number of titles available
        # per page in the subject's bookshelf.
        MAX_PAGE_RESULTS = 25

        # Build the URL to scrape from the subject based on the subject to bookshelf
        # dictionary.
        bookshelf_value = self.subject_to_bookshelf[subject]
        subject_url = "https://www.gutenberg.org/ebooks/bookshelf/" + str(bookshelf_value) +\
                        "?start_index="

        # Initialize a few counter variables such as a page counter, text counter
        # and a boolean that represents whether or not a page is empty (initialized
        # to False).
        text_counter = 0
        page_empty = False
        page_counter = 0

        # Continue scraping from this subject as long as the text limit has not been
        # reached and the resulting page is not empty.
        while text_counter != limit and not page_empty:
            # Build the specific URL for the page in the subject.
            page_url = subject_url + str(1 + (page_counter * MAX_PAGE_RESULTS))

            # Send a request to the page.
            page_response = requests.get(page_url)

            # Get the return status code.
            if page_response.status_code != 200:
                print("Error: Recieved status code " + str(page_response.status_code) + " from " +\
                        page_url)
                break

            # Get the beautifulsoup object from the html.
            page_soup = bsoup(page_response.content, features="lxml")

            # Get the list of all links to the titles in a page.
            link_elements = page_soup.find_all("li", {"class": "booklink"})

            # Check the number of texts that are available from the page. If there
            # are no texts available on the page, then set the empty page boolean to
            # True. This will cause the program to exit the while loop.
            if len(link_elements) == 0:
                page_empty = True

            # For each link element, extract the URL extension to that text, along with
            # the text title.
            for link in link_elements:
                text_link = link.find("a")["href"]
                text_title = link.find("span", {"class": "title"}).text.replace("\n", "")

                # Use the text URL extension and its title to download the text. Increment
                # the text counter.
                self.download_text_file(text_link, text_title, subject)
                text_counter += 1

                # If the text counter has reached the limit, break from the for loop. After
                # breaking from the loop, the program should also exit the parent while
                # loop.
                if text_counter == limit:
                    break

            # Increment the page counter.
            page_counter += 1

        # Return the function.
        return


    # Download all available texts from all subjects.
    # @param: limit_per, an integer value representing the maximum number of texts
    #   to be downloaded per subject. Default value is None.
    # @param: limit_total, an integer value representing the maximum number of texts
    #   to be downloaded from all subjects. Default value is None.
    # @return: Returns nothing.
    def download_all_fiction(self, limit_per=None, limit_total=None):
        # Check whether the limit arguments were set and pull from each subject
        # accordingly.
        if limit_per != None:
            # If a limit per subject was set, pass that limit along in the arguments.
            for subject in self.valid_subjects:
                self.download_from_subject(subject=subject, limit=limit_per)
        elif limit_total != None:
            # If the total limit was set, divide that by the number of available
            # available subjects and pass the integer result as the limit in the
            # arguments.
            limit_per = limit_total // len(list(self.subject_to_bookshelf.keys()))
            for subject in self.valid_subjects:
                self.download_from_subject(subject=subject, limit=limit_per)
        else:
            # If no limit was set, just download all the content from the subject
            # (NOTE: This is not recommended unless you have Terabytes of storage).
                for subject in self.valid_subjects:
                        self.download_from_subject(subject=subject)

        # Return the function.
        return


class AO3():
    def __init__(self):
        # Initialize the URL to scrape from (this provides a general search of AO3
        # where the only parameter is that the results are complete and in English.
        self.raw_url = "https://archiveofourown.org/works/search?utf8=%E2%9C%93&commit=" +\
                            "Search&work_search%5Bquery%5D=&work_search%5Btitle%5D=" +\
                            "&work_search%5Bcreators%5D=&work_search%5Brevised_at%5D=" +\
                            "&work_search%5Bcomplete%5D=T&work_search%5Bcrossover%5D=" +\
                            "&work_search%5Bsingle_chapter%5D=0&work_search%5Bword_count%5D=" +\
                            "&work_search%5Blanguage_id%5D=en&work_search%5Bfandom_names%5D=" +\
                            "&work_search%5Brating_ids%5D=&work_search%5Bcharacter_names%5D=" +\
                            "&work_search%5Brelationship_names%5D=" +\
                            "&work_search%5Bfreeform_names%5D=&work_search%5Bhits%5D=" +\
                            "&work_search%5Bkudos_count%5D=&work_search%5Bcomments_count%5D=" +\
                            "&work_search%5Bbookmarks_count%5D=&work_search%5Bsort_column%5D=" +\
                            "_score&work_search%5Bsort_direction%5D=desc"
        self.base_url = "https://archiveofourown.org/works/search?utf8=%E2%9C%93&commit=Search" 

        # Initialize a dictionary of parameters that can be set in the search. First
        # isolate the criteria in a list. Then clean that list. For each value
        # remaining (a valid criteria) add that to the dictionary and set its value
        # to an empty string ("").
        self.criteria = {}
        keys = self.raw_url.replace("%5B", "+").replace("%5D", "+").split("+")
        for key in keys:
            if "=" in key:
                keys.remove(key)

        for valid_key in keys:
            self.criteria[valid_key] = ""

        # Some values of the dictionary should be set, such as the language.
        self.criteria["language"] = "en"


    # Download the specified text.
    # @param: link_extension, the URL extension to the text's download page.
    # @param: title, the title of the text.
    # @return: Returns nothing.
    def download_text_file(self, link_extension, title):
        # Build the URL to scrape from the text page.
        text_url = "https://www.archiveofourown.org" + link_extension

        # Send a request to the page.
        page_response = requests.get(text_url)

        # Get the return status code.
        if page_response.status_code != 200:
            print("Error: Recieved status code " + str(page_response.status_code) + " from " +\
                    text_url)
            return

        # Get the beautifulsoup object from the html.
        page_soup = bsoup(page_response.content, features="lxml")

        # Get the download element from the page.
        download_element = page_soup.find("li", {"class": "download"})


        # From the downloadab element, extract the entries that have the URL extensions
        # for the different download sources. Iterate over the contents of each entry.
        entries = download_element.find_all("li")
        for entry in entries:
            # Extract the link for the download source.
            link = entry.find("a")["href"]
            link_text = entry.find("a").text

            # If the link for the download source is HTML, send a request to the download
            # source and save the response (the text) to a file.
            if link_text.replace("\n", "") == "HTML": 
                download_response = requests.get("https://www.archiveofourown.org" + link)

                # Get the return status code.
                if download_response.status_code != 200:
                    print("Error: Recieved status code " + str(download_response.status_code) +\
                            " for downloading text " + title)
                    return

                # The content of the request should contain all of the text within
                # the title. Be sure to clean it up if necessary.
                download_content = bsoup(download_response.content, features="lxml").text
                download_content = download_content.replace("\r\n", "\n")

                # Some housekeeping in regards to files. Check for an AO3 directory. Make
                # the directory it doesn't exist.
                if not os.path.exists("AO3") or not os.path.isdir("AO3"):
                    os.mkdir("AO3")

                # Some housekeeping in regards to the title. Certain characters are not
                # allowed in file names.
                title = title.replace("\r", "").replace("?", "").replace(":", "-")
                title = title.replace("*", "").replace("\"", "").replace("/", "-")
                title = title.replace("|", "")
                
                # Create the file name. Open and write to the new file under that name.
                file_name = "./AO3/" + title + ".txt"
                file = open(file_name, "w+", encoding="utf-8")
                file.write(download_content)
                file.close()

                # Return the function.
                return

        # Return the function.
        return

    
    # Download all available texts.
    # @param: limit, an integer value representing the maximum number of texts to be
    #   downloaded. Default value is 10000.
    # @param: word_count, the minimum number of words a text should have if it is to
    #   be downloaded. Default value is 5000
    # @param: hits, the minumum number of hits a textu should have if it is to be
    #   downloaded. Default value is 5000
    # @param: sort, how to sort the results. Default value is "desc" (descending).
    # @param: complete, a boolean value representing whether the texts downloaded need
    #   to be completed. Default value is "T" (True).
    # @return: Returns nothing.
    def download_from_ao3(self, limit=10000, word_count=5000, hits=5000, sort="desc", complete="T"):
        # Update the search criteria based on the arguments.
        self.criteria["word_count"] = str(word_count)
        self.criteria["hits"] = str(hits)
        self.criteria["sort_direction"] = sort
        self.criteria["complete"] = complete

        # Initialize a few counter variables such as a page counter and text counter.
        text_counter = 0
        page_counter = 1

        # Continue scraping from this search as long as the text limit has not been
        # reached.
        while text_counter <= limit:
            # Built the search URL based on the search criteria.
            #self.base_url = "https://archiveofourown.org/works/search?utf8=%E2%9C%93&commit=Search" 
            search_url = self.base_url + "&page=" + str(page_counter) 
            for key, value in self.criteria.items():
                if key == "limit" or key == "word_count" or key == "hits":
                    search_url += "&work_search%5B" + key + "%5D=%3E" + value
                else:
                    search_url += "&work_search%5B" + key + "%5D=" + value

            # Send a request to the page.
            search_response = requests.get(search_url)

            # Get the return status code.
            if search_response.status_code != 200:
                print("Error: Recieved status code " + str(search_response.status_code) + " from " +\
                        search_url)
                return

            # Get the beautifulsoup object from the html.
            results_soup = bsoup(search_response.content, features="lxml")

            # Get the number of search results returned. Restrict the limit entered from
            # the arguments if that value exceeds the search results.
            results_elements = results_soup.find_all("h3", {"class": "heading"})
            for element in results_elements:
                if "Found" in element.text:
                    results_count = element.text.split()[0]
            if limit > int(results_count):
                limit = results_count

            # Get the list of all links to the titles in a page.
            link_elements = results_soup.find_all("li", {"class": "work blurb group"})

            # For each link element, extract the URL extension to that text, along with
            # the text title.
            for link in link_elements:
                text_link = link.find("a")["href"]
                text_title = link.find("a").text.replace("\n", "")

                print("Texts collected: " + str(text_counter))
                print("Page number: " + str(page_counter))
                print("Text limiter: " + str(limit))
                print("Text link: " + text_link)
                print("Text title: " + str(text_title.encode("utf-8")))
                print("+" * 32)

                # Use the text URL extension and its title to download the text. Increment
                # the text counter.
                self.download_text_file(text_link, text_title)
                text_counter += 1

                # If the text counter has reached the limit, break from the for loop. After
                # breaking from the loop, the program should also exit the parent while
                # loop.
                if text_counter > limit:
                    break

            # Increment the page counter and give a pause before scraping from the next
            # search results page.
            page_counter += 1
            time.sleep(150)

        # Return the function. 
        return


def main():
    '''
    # Intialize the Gutenberg object and scrape the desired amount of texts from there.
    gut_obj = Gutenberg()

    # Test getting the list of valid subjects from the Fantasy section.
    print("Subjects list:")
    print(json.dumps(gut_obj.valid_subjects, indent=4))

    # Test getting the mapping of subjects to their bookshelf value.
    print("Subjects to bookshelf mapping:")
    print(json.dumps(gut_obj.subject_to_bookshelf, indent=4))

    # Test downloading from a subject (in this case Gothic Fiction).
    gut_obj.download_from_subject(gut_obj.valid_subjects[0])

    # Test downloading from all subjects.
    gut_obj.download_all_fiction()
    '''

    # Initialize an AO3 object and scrape the desired amount of texts from there.
    ao3 = AO3()

    # Test getting the mapping of search criteria to their value.
    print("Search criteria mapping:")
    print(json.dumps(ao3.criteria, indent=4))

    # Test downloading from AO3.
    ao3.download_from_ao3()

    # Exit the program.
    exit(0)


if __name__ == '__main__':
    main()
