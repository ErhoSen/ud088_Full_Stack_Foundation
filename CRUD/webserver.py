from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


class webServerHandler(BaseHTTPRequestHandler):
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.bind = engine
    DBsession = sessionmaker(bind=engine)
    session = DBsession()

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>Make a New Restaurant Here</a><br/><br/>"
                restaurants = self.session.query(Restaurant).all()
                for rest in restaurants:
                    output += "<p>%s</p>" % rest.name
                    output += "<a href='/restaurants/{0}/edit'>edit</a><br/><a href='/restaurants/{1}/delete'>delete</a>".format(rest.id, rest.id)
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><input name="restaurant_name" type="text"><input type="submit" value="Create!"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurant_id = self.path.split('/')[2]
                print restaurant_id
                restaurant = ""
                if restaurant_id.isdigit():
                    restaurant = self.session.query(Restaurant).filter_by(id=restaurant_id)[0].name
                else:
                    print "Something wrong!"
                    restaurant = "Default Restaurant"
                output = ""
                output += "<html><body>"
                output += "<h2>" + restaurant + "</h2>"
                output += '''<form method='POST' enctype='multipart/form-data' action='%s'><input name="restaurant_name" type="text"><input type="submit" value="Rename!"> </form>''' % self.path
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurant_id = self.path.split('/')[2]
                print restaurant_id
                restaurant = ""
                if restaurant_id.isdigit():
                    restaurant = self.session.query(Restaurant).filter_by(id=restaurant_id)[0].name
                else:
                    print "Something wrong!"
                    restaurant = "Default Restaurant"
                output = ""
                output += "<html><body>"
                output += "<h2>Are you sure you want to delete " + restaurant + "?</h2>"
                output += '''<form method='POST' enctype='multipart/form-data' action='%s'><input type="submit" value="Delete!"> </form>''' % self.path
                output += "</body></html>"
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                restaurant_id = self.path.split('/')[2]
                if restaurant_id.isdigit():
                    restaurant = self.session.query(Restaurant).filter_by(id=restaurant_id).one()
                else:
                    print "Something wrong!"
                    raise Exception
                self.session.delete(restaurant)
                self.session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                messagecontent = ""
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant_name')
                print messagecontent
                restaurant_id = self.path.split('/')[2]
                restaurant = ""
                if restaurant_id.isdigit():
                    restaurant = self.session.query(Restaurant).filter_by(id=restaurant_id)[0]
                else:
                    print "Something wrong!"
                    raise Exception
                restaurant.name = messagecontent[0]
                self.session.add(restaurant)
                self.session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                messagecontent = ""
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant_name')
                print messagecontent
                newRestaurant = Restaurant(name = messagecontent[0])
                self.session.add(newRestaurant)
                self.session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s"  % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()