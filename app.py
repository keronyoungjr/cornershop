import os
from flask import Flask, render_template, redirect, url_for
from forms import SearchForm
from algorithms.stores import Global
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Adj34395zAheregi0z'


@app.route('/', methods=('GET',))
def index():
    return render_template('index.html')

@app.route('/search', methods=('POST',))
def search():
    form = SearchForm(csrf_enabled=False)

    if form.validate_on_submit():
        crawler = Global()
        findings = crawler.search(form.item.data)
        return render_template('store.html', products=findings)

    return redirect(url_for('index'))


@app.route('/laptops', methods=('GET',))
def laptops():
    crawler = Global()
    findings = crawler.search('laptop')
    return render_template('store.html', products=findings)


@app.route('/smartphones', methods=('GET',))
def smartphones():
    crawler = Global()
    findings = crawler.search('smartphone')
    return render_template('store.html', products=findings)


@app.route('/cameras', methods=('GET',))
def cameras():
    crawler = Global()
    findings = crawler.search('camera')
    return render_template('store.html', products=findings)


@app.route('/accessories', methods=('GET',))
def accessories():
    crawler = Global()
    findings = crawler.search('accessory')
    return render_template('store.html', products=findings)

@app.route('/about us')
def about_us():
    return render_template('about us.html')

@app.route('/contact us')
def contact_us():
    return render_template('contact us.html')


@app.route('/store')
def store():
#    crawler = Global()
#    findings = crawler.search('accessory')
    return render_template('store.html')


app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 9000)))


if __name__ == '__main__':
    app.run()#debug=True, port=9000, host="0.0.0.0")
    app.debug=True