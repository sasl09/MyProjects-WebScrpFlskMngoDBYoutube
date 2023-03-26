from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

#Start Flask
application = app = Flask(__name__) # initializing a flask app

#Create index (home page)
@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

#Create review page (for displaying results)
@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","") #get input in search form without spaces
            youtube_url = "https://www.flipkart.com/search?q=" + searchString #add last var to main url
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read() #open url
            uClient.close() #then close it (this is good practice)
            flipkart_html = bs(flipkartPage, "html.parser") #get HTML from url page and beautify it
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"}) #get divs with that class
            # del bigboxes[27:30] #delete last 3 divs as they aren't products
            del bigboxes[0:3] #and neither are the first 3
            box = bigboxes[0] #Get the main div or box
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] #get only the urls of products
            #from page with results from search
            prodRes = requests.get(productLink) #go to url of product and get http response (in case of error)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser") #get only the text from HTML of page of product and beutify it
            print(prod_html) #just so that you can see it in the console
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"}) #from page of product, get all comment
            #boxes
            # del commentboxes[10::] #keep only first 10 divs, as the last 2 are not comments

            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'

                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text

                except Exception as e:
                    print("Exception while creating dictionary: ", e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)


                #This creates a csv file but it makes it ugly

                # import pandas as pd
                # import json
                # filename = searchString + ".csv"
                # fw = open(filename, "w")
                # headers = "Product, Customer Name, Rating, Heading, Comment \n"
                # fw.write(headers)
                # for i in reviews:
                #     fw.write(json.dumps(i))
                #     print(i)


                #This is the good one
                # create a csv file called test.csv and
                # store it a temp variable as outfile
                import csv
                filename = searchString + ".csv"
                with open(filename, "w") as outfile:

                    # pass the csv file to csv.writer.
                    writer = csv.writer(outfile)

                    # convert the dictionary keys to a list
                    key_list = list(reviews[0].keys())
                    print(key_list)

                    # find the length of the key_list
                    limit = len(key_list)

                    # the length of the keys corresponds to
                    # no. of. columns.
                    writer.writerow(reviews[0].keys())
                    print("All good til here")

                    # iterate each column and assign the
                    # corresponding values to the column
                    import emoji #This will convert emojis to txt, and it could convert the txt back to emoji
                    for i in reviews:
                        print(i)
                        # writer.writerow([i[x].encode(encoding='utf-8') for x in key_list])
                        writer.writerow([emoji.demojize(i[x]) for x in key_list])

            #Make a MongoDB connection and upload your searches
            client=pymongo.MongoClient("mongodb+srv://ebriosapiens:passwordhere@cluster0.grhjwx6.mongodb.net/?retryWrites=true&w=majority")
            db = client['review_scrap']
            review_col = db['review_scrap_data']
            review_col.insert_many(reviews)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])

        #This is the main exception should something go wrong
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'

    #This will just make sure that if we don't make a post request our page will return to index.
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
	#app.run(debug=True)