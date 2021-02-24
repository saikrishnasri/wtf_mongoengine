#
#  example Flask app that uses MongoEngine
#
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file
)
from flask_wtf.csrf import CSRFProtect
from flask_mongoengine import MongoEngine


#########################
#
#  SETUP FLASK and JINJA2
#
#########################

app = Flask(__name__)

def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)
app.jinja_env.filters['datetime'] = datetimeformat

#########################
#
#  SETUP CSRF
#
#########################

app.config['SECRET_KEY'] = "my super secret key"
csrf = CSRFProtect(app)

#########################
#
#  SETUP MONGOENGINE
#
#########################

app.config['MONGODB_DB'] = "wtf_mongoengine"

db = MongoEngine(app)

#########################
#
#  MONGOENGINE CLASSES
#
#########################

class Picture(db.EmbeddedDocument):
    caption = db.StringField()
    image = db.ImageField(image_size=(400, 200, False), thumbnail_size=(40, 40, True))

class PageContent(db.Document):
    name = db.StringField()
    firstName=db.StringField()
    lastName =db.StringField()
    tagline = db.StringField()
    pictures = db.EmbeddedDocumentListField(Picture)


#########################
#
#  PUBLIC ROUTES
#
#########################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page1')
def page_one():
    doc = PageContent.objects(name='page1').first()
    if not doc:
        doc = PageContent()
        doc.name = 'page1'
        doc.tagline = 'default for page 1'
        doc.pictures = []
        doc.save()
    return render_template('page1.html', doc=doc)

# @app.route('/page2')
# def page_two():
#     doc = PageContent.objects(name="page2").first()
#     if not doc:
#         doc = PageContent()
#         doc.name = 'page2'
#         doc.tagline = 'this is page 2'
#         doc.pictures = []
#         doc.save()
#     return render_template('page1.html', doc=doc)

@app.route('/upload/<pagename>', methods=['GET', 'POST'])
def upload(pagename):
    errmsg = ""
    doc = PageContent.objects(name=pagename).first()
    if 'upload_picture' in request.form:
        if 'picture_file' in request.files:
            pic = Picture()
            pic.caption = request.form['caption']
            doc.firstName=request.form['firstName']
            doc.lastName=request.form['lastName']
            pic.image.put(request.files['picture_file'])
            doc.pictures.append(pic)
            doc.save()
            return redirect(url_for("index"))
        else:
            errmsg = 'File not selected.'
    return render_template(
        'upload_picture.html',
        doc=doc,
        errmsg=errmsg
    )

@app.route('/img/<doc_name>.<index>.png')
def get_pic(doc_name, index):
    doc = PageContent.objects(name=doc_name).first()
    i = int(index)
    pic = doc.pictures[i]
    # send_file will invoke the "read()" function of pic.image
    return send_file(pic.image, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True,port=8000)