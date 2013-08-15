'''
Created on Aug 4, 2013

@author: rajath
'''
import os
import getpass
import re
import lxml.html
from xml.sax import saxutils
import xml.etree.ElementTree as et
import logging

# TODO: write a function to map facebook user-ids with their usernames
# and display them while searching for a username

dir_path = ''

# Source file path
src_file_path = os.getcwd()

# Get username on Linux system
username = getpass.getuser()
log_path = '/home/' + username + '/.purple/logs/jabber'
buddy_list_file = '/home/' + username + '/.purple/blist.xml'

re_exp = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

accounts = []
users = []
urls_dict = {}
fb_user_map = {}

# Map Facebook userIds with names since log file names have numbers in them
# Do an initial scan of the userIds and store it in a dictionary
# To be called after scanning accounts
def map_user_ids(accounts):
    users_dict = {}
    tmp = os.getcwd()
    tree = et.parse(buddy_list_file)
    root = tree.getroot()
    users = []
    for account in accounts:
        users = root.findall(".//*[@account='" + account + "/']")
        for user in users:
            try:
                alias = user.find('alias').text
                name = user.find('name').text
                if not users_dict.has_key(alias):
                    user_id = [name]
                    users_dict[alias] = user_id
                else:
                    user_id = users_dict[alias]
                    id.append(name)
                    users_dict[alias] = user_id
            except:
                # For some facebook ids, usernames are not available. Handle it in logs
                pass
    # Switch back to the previous directory    
    os.chdir(tmp)
    return users_dict
    
# Extracts URL from a ping
def extract_url(line):
    # Identify URL and extract it
    refined_url = re.findall(re_exp, line)
    if len(refined_url) == 0:
        # throw exception
        pass
    return list(set([i.strip('<br/>').strip('</a>') for i in refined_url]))

# Searches for users based on the search term provided in the input
def search_users(accounts, search_term):
    global dir_path
    user_id = users_dict[search_term]
    for i in accounts:
        dir_path = log_path + '/' + i
        os.chdir(dir_path)

        for j in os.listdir(dir_path):
            for user in user_id:
                if user in j:
                    users.append(i + '/' + j)
                    break

    return users

# Lists different accounts for which logs are available
def list_accounts(log_path):
    for i in os.listdir(log_path):
        accounts.append(i)
    return accounts

def get_links(users):
    # Search in all accounts for that user. For example, the user may have accounts
    # in both gmail and facebook. The following code will search in both.
    for i in users:
        log_files_path = log_path + '/' + i
        os.chdir(log_files_path)
        for filename in os.listdir(log_files_path):
            date = filename.split('.')[0]
            f = open(filename)
            lines = f.readlines()
            f.close()
            for line in lines:
#                 if 'www' in line:
                if re.findall(re_exp, line):
                    if not urls_dict.get(date):
                        url_list = []
                    else:
                        url_list = urls_dict[date]
                    urls_dict[date] = url_list + extract_url(line)
    return urls_dict

# Get the title of the URL to display it more meaningfully
def get_url_title(url):
    try:
        t = lxml.html.parse(url)
    except:
        return url
    title = t.find(".//title").text
    return saxutils.escape(title)

# If it's a YouTube URL, embed the video in the output HTML
def embed_youtube_video(yt_link):
    yt_link = yt_link.replace('watch?v=','embed/')
    yt_link = yt_link[yt_link.find('www'):]
    embed_text = '<iframe width="560" height="315" src="http://' + yt_link + '" frameborder="0" allowfullscreen></iframe>'

    return embed_text
    
# Replace placeholders in HTML stub with actual links and corresponding dates
def insert_links_in_html(urls):
    output = ''
    for k, v in urls.iteritems():
        date = '<h2>' + k + '</h2>'
        links = ''
        for link in v:
            if 'youtube' in link:
                embed_link = embed_youtube_video(link)
                links += '<ul>' + get_url_title(link) + '<br/>' + embed_link + '</ul>'
            else:
                links += '<ul> <a href="' + link + '">' + get_url_title(link) + '</a></ul>'
        output += date + links
    return output

# Generate HTML from stub with links and dates replaced
def generate_html(urls):
    global users
    # Stubbed HTMLs are found in data folder in src directory.
    # Temporarily 'cd'ing to this directory
    tmp = os.getcwd()
    os.chdir(src_file_path)
    html_stub = open('data/html_stub.html')
    generated_html = open('data/output_html.html', 'w')
    for line in html_stub:
        generated_html.write(line.replace('[INSERT_LINKS_HERE]',insert_links_in_html(urls)))
    html_stub.close()
    generated_html.close()
    os.chdir(tmp)
    return generated_html

accounts = list_accounts(log_path)

print 'Accounts Found: ', accounts

users_dict = map_user_ids(accounts)

search_term = raw_input('Search username:')

users = search_users(accounts, search_term)

if len(users) != 0:
    print 'Users found:', users
else:
    print 'No logs found'

urls = get_links(users)

generate_html(urls)
print 'Output file generated!'