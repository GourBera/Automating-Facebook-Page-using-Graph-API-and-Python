import facebook
from setuptools import setup
from facepy import GraphAPI
from facepy.exceptions import *
import sqlite3, time
from textblob import TextBlob
from SendMail.testMail import *


# Sentiment Analysis

def sentiment(text):
    v = TextBlob(text).sentiment.polarity
    return "%.2f" % v

# Posting Comments

def PostComment(page_token, statusid):
    graph = facebook.GraphAPI(page_token)
    graph.put_object(statusid, "comments", message="Will get back to you soon!!")
    print("commented!")

# TestProject

def IncidentMgmt(access_token, pageId, page_token):
    graph = GraphAPI(access_token)
    #data = graph.get("122075815230302?fields=feed{message,comments}")
    data = graph.get(pageId + "?fields=feed{message,comments}")

    db = sqlite3.connect("IncidentMgmt.db")
    c = db.cursor()

    c.execute("""DROP TABLE PostWithComments""")
    c.execute("""CREATE TABLE PostWithComments(postno INTEGER PRIMARY KEY, post TEXT, postid VARCHAR(50) NOT NULL, postcreacreatedtime VARCHAR(50), postedbyname VARCHAR(255), postedbyid VARCHAR(50), score REAL(50))""")
    c.execute("""DROP TABLE PostWithOutComments""")
    c.execute("""CREATE TABLE PostWithOutComments(postno INTEGER PRIMARY KEY, post TEXT, postid VARCHAR(50) NOT NULL, score REAL(50))""")
    c.execute("""DROP TABLE Comments""")
    c.execute("""CREATE TABLE Comments(commentsNo INTEGER PRIMARY KEY, postid VARCHAR(50) NOT NULL, comments TEXT, commentsid VARCHAR(50) NOT NULL, commentscreacreatedtime VARCHAR(50), commentedbyname VARCHAR(255), commentedbyid VARCHAR(50), score REAL(50))""")

    for d in data['feed']['data']:
    
        print('*************************************************')
        print('Post:' + d['message'])
        print('PostID:' + d['id']) 
        post = d['message']
        score = float(sentiment(post))
     
    
        if score < -0.50:
            PostComment(page_token, d['id'])
            send_Mail('gour.bera@hpe.com', 'Immediate Response required', "Some one posted the below message:\n"+post)
            
    
		# Creating db
        db = sqlite3.connect("IncidentMgmt.db")
        c = db.cursor()
    
        try:
            postdetail = d['comments']['data']
        
            dt = postdetail[0]['created_time']
            datetime = dt[0:10] + ' ' + dt[11:19]
        
            print('Post Created Time: ' + datetime)
            print('Posted By Name: ' + postdetail[0]['from']['name'])
            print('Posted By ID: ' + postdetail[0]['from']['id']) 
            print("Score: " + str(score))
        
            dbdata = d['message'], d['id'], datetime, postdetail[0]['from']['name'], postdetail[0]['from']['id'], float(score)
        
            c.execute('INSERT INTO PostWithComments(post, postid, postcreacreatedtime, postedbyname, postedbyid, score) VALUES(?,?,?,?,?,?)', dbdata)
            db.commit()
        
            print('*************************************************')
            print('---------------------------------------------')
            print() 
    
            cmt = d['comments']   
            for c in cmt['data']:
                # print(c)
                print('Comments: ' + c['message'])
                print('CommentsID: ' + c['id']) 
            
                dt = c['created_time']
                datetime = dt[0:10] + ' ' + dt[11:19]
            
                print('Comments Created Time: ' + datetime)
                print('Comented By Name: ' + c['from']['name'])
                print('Comented By ID: ' + c['from']['id'])
            
                score = float(sentiment(c['message']))
            
                if score < -0.50:
                    PostComment(page_token, c['id'])
                    send_Mail('gour.bera@hpe.com', 'Immediate Response required', "Some one posted the below Comment:\n"+c['message'])
                print("Score: " + str(score))
            
                dbdata = d['id'], c['message'], d['id'], datetime, c['from']['name'], c['from']['id'], float(score)
            
                db = sqlite3.connect("IncidentMgmt.db")
                c = db.cursor()
            
                c.execute('INSERT INTO Comments(postid, comments, commentsid, commentscreacreatedtime, commentedbyname, commentedbyid, score) VALUES(?,?,?,?,?,?,?)', dbdata)
                db.commit()
            
                print()
                print()
            
        except:
        
            print("Score: " + str(score))
            print()
            print('No Comments for this Post..')
            #print(d['message'], d['id'], str(score), ' No comments for this Post')   
        
            dbdata = d['message'], d['id'], float(score)
        
            db = sqlite3.connect("IncidentMgmt.db")
            c = db.cursor()
        
            c.execute('INSERT INTO PostWithOutComments(post, postid, score) VALUES(?,?,?)', dbdata)
            db.commit()
        
            print()
            print()
          
if __name__ == '__main__':
	access_token = ""
	pageId = ""
	page_token = ""
	
    IncidentMgmt(access_token, pageId, page_token)