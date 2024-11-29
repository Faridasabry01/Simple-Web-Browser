from datetime import datetime
from tkinter import *
from tkinter import messagebox
from tkinter.tix import IMAGETEXT
from urllib.request import urlopen
from cefpython3 import cefpython as cef
import sys
from PIL import Image, ImageTk
import socket
from urllib.parse import urlparse


URL = ""
isSearch = True # to know whether coming from bakward or forward
window = 0 # the global window of scrren 
backward = [] #array of backward windows
forward = [] #array of forward windows
bookmarks = [] #array of bookmarks
history = [] #array of all windows that was opened
shown = True # flag to show bookmarks
Labels = [] # labels of bookmarks


#function to open the url of selected bookmark
def callback(i):
    global URL, isSearch
    URL = bookmarks[i]
    isSearch = False
    browse()
    isSearch = True


#show all the bookmarks and make it clickable to open the url of it
def show_bookmark():
    global bookmarks,shown, Labels
    # Create indices  
    if (shown):
        indices = list(range(0, len(bookmarks)))

        # Create label buttons
        for i in indices:
            label = Label(window, text=bookmarks[i],
                        bg="white", fg="black", borderwidth=2)
            label.bind("<Button-1>", lambda event, index=i: callback(index))
            label.pack(pady=10, padx=10)
            
            Labels.append(label)
        shown = False
    else:    
        shown = True
        for label in Labels:
            label.destroy()

#check of the saved bookmarks and add a new one when clicked
def save_bookmark():
    global bookmarks, URL
    if (URL not in bookmarks):
        bookmarks.append(URL)


#function to open the url
def open_link(url):
    print(url)
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    cef.CreateBrowserSync(url=url, window_title=url)
    cef.MessageLoop()


# to open the previus url from the top of the arry bakward and append it to array forward
def go_back():
    global backward, forward, URL, isSearch
    if (len(backward) > 0):
        isSearch = False
        forward.append(backward[-1])
        URL = backward.pop()
        browse()
        isSearch = True


 #to open the previus url from the top of the arry forward and append it to array backward
def go_forward():
    global backward, forward, URL, isSearch
    if (len(forward) > 0):
        isSearch = False
        backward.append(forward[-1])
        URL = forward.pop()
        browse()
        isSearch = True


#==============================================
#to show the histroy array elements in a html format
def show_history():
    global history, URL
    listHistory = list(range(0, len(history)))

    f = open("history.html", "w")
    f.write("<html> <head><link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css\" rel=\"stylesheet\" integrity=\"sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi\" crossorigin=\"anonymous\"></head><body><nav class=\"navbar navbar-expand-lg navbar-light bg-dark\"><!-- Container wrapper --><div class=\"container-fluid\"><!-- Toggle button --><button class=\"navbar-toggler\"type=\"button\"data-mdb-toggle=\"collapse\"data-mdb-target=\"#navbarCenteredExample\"aria-controls=\"navbarCenteredExample\"aria-expanded=\"false\"aria-label=\"Toggle navigation\"><i class=\"fas fa-bars\"></i></button><div class=\"collapse navbar-collapse justify-content-center\"id=\"navbarCenteredExample\"><ul class=\"navbar-nav mb-2 mb-lg-0\"><li class=\"nav-item\"><a class=\"nav-link active\" aria-current=\"page\" href=\"History.html\" style=\"color:white\"><h3>History</h3></a></li></ul></div></div></div></nav><ul>")
    for i in listHistory:
        f.write("<li>")
        f.write(history[i])
        f.write("</li>")
    f.write("</ul></body></html>")
    f.close()
    open_link("file:///history.html")


# clear the array history
def clear_history():
    global history
    history.clear()
#=====================================================


# Define browse function
def browse():
    global backward, forward, URL
    # Get URL from text box

   # to ensure where the URL came from 
    if (isSearch):
        URL = url_entry.get()
        backward.append(URL)
        forward.clear()

    try:
        # format validation
        if (URL[0] != 'h') and (URL[0] != 'H'): 
            if URL[0] != 'w' and URL[0] != 'W':  # url does't start w/ www
                parsed_url = urlparse('http://www.' + URL)
            else:
                parsed_url = urlparse('http://' + URL)
        else: 
            if URL[7] != 'w' and URL[7] != 'W':  # url does't start w/ www
                parsed_url = urlparse('http://www.' + URL[7:])
            else:
                parsed_url = urlparse(URL)
        host = parsed_url.netloc # ex: WWW.Google.com
        # ==============================================
        filePath = parsed_url.path # the rest of URL
        if filePath is None:  # no file path in URL
            filePath = ''
        port = 80 #port of browser range from 80 to 8080
        # =============

        # create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP IP version 4

        # connect to the server using the socket object
        client_socket.connect((host, port))

        # send an HTTP GET request to the server
        request = 'GET {} HTTP/1.0\r\nHost: {}\r\n\r\n'.format(filePath, host)

        client_socket.send(request.encode())



        #add URL to history list with time stamp
        hist=URL + " " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        history.append(hist)


        # receive the response from the server
        response = b'' #stands for bytes
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            response += data

        client_socket.close()

        # Open URL
        # decode the response
        text = response.decode()
        

       # the default is error 404
        with open('web.html', 'w') as f:
            f.write(
                "<!DOCTYPE html> <html><head><title>404 Not Found</title></head> <body><h1>404 Not Found</h1><p>The requested URL was not found on this server.</p> </body></html>")

     #save the response in html file
        for i in range(len(text)):
            #to begin save after html tag
            if text[i:i + 6] == "<!doct" or text[i:i + 6] == "<!DOCT" or text[i:i + 6] == "<html>" or text[
                                                                                                      i:i + 6] == "<HTML>":
                with open('web.html', 'w') as f:
                    f.write(text[i:])
                break

        open_link("file:///web.html")

    except Exception as e:
        # Show error message
        messagebox.showerror("Error", e)





# our main program
# Create window
window = Tk()
window.title('Web Browser')
window.geometry('1920x1080')
window.wm_state('zoomed')

# Add background image
bg_image = Image.open("wallpaperflare.com_wallpaper.png")
bg_image = bg_image.resize((1600, 900), Image.ANTIALIAS)
bg = ImageTk.PhotoImage(bg_image)
bg_label = Label(image=bg)
bg_label.place(x=0, y=0)

# Create url box     
url_image = Image.open("wallpaperflare.com_wallpaper2.png")
url_img = url_image.resize((658, 35), Image.ANTIALIAS)
url = ImageTk.PhotoImage(url_img)
url_label = Label(image=url)
url_label.place(x=475, y=218)
url_entry = Entry(width=100)
url_entry.place(x=500, y=228.2) # the search box placeholder

# Create search button
goPhoto = PhotoImage(file = r"images\searchButton.png")
go_button = Button(window, width=180, height=70,
                   pady=5, padx=5, image= goPhoto,
                   text="Search!", command=browse)

go_button['font'] = ('Helvetica', 20)




# create backward button
backPhoto = PhotoImage(file = r"images\backwardButton.png")
back_button = Button(window, width=50, height=50,
                     pady=5, padx=5, image=backPhoto,
                     text="back!", command=go_back)

back_button['font'] = ('Helvetica', 20)


# create forward button
forwardPhoto = PhotoImage(file = r"images\forwardButton.png")
forward_button = Button(window, width=50, height=50,
                     pady=5, padx=5, image=forwardPhoto,
                        text="forward!", command=go_forward)

forward_button['font'] = ('Helvetica', 20)


# create add_bookmark button
favPhoto = PhotoImage(file = r"images\saveBookmark.png")
fav_button = Button(window, width=80, height=90,
                     pady=5, padx=5, image=favPhoto,
                    text="save bookmark", command=save_bookmark)

fav_button['font'] = ('Helvetica', 20)



# create show_bookmark button
showFavPhoto = PhotoImage(file = r"images\BookmarkButton.png")
show_fav_button = Button(window, width=80, height=90,
                     pady=5, padx=5, image=showFavPhoto,
                         text="show bookmark", command=show_bookmark)

show_fav_button['font'] = ('Helvetica', 20)




# create Show_histroy button
historyPhoto = PhotoImage(file = r"images\historyButton.png")
history_button = Button(window, width=80, height=80,
                     pady=5, padx=5, image=historyPhoto,
                        text="Show History", command=show_history)

history_button['font'] = ('Helvetica', 20)




# create clear_history button
clearHistoryPhoto = PhotoImage(file = r"images\clearHistory.png")
historyClear_button = Button(window, width=140, height=60,
                     pady=5, padx=5, image=clearHistoryPhoto,
                        text="clear History", command=clear_history)

historyClear_button['font'] = ('Helvetica', 20)


#places of buttons
fav_button.place(x=1300, y=205)
show_fav_button.place(x=1300, y=320)
go_button.place(x=705, y=350)
back_button.place(x=150, y=205 )
forward_button.place(x=300, y=205)
history_button.place(x=755, y=500)
historyClear_button.place(x=725, y=600)
window_width = window.winfo_width()

# Run application
window.mainloop()
