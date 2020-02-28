from flask import Flask, render_template, request, redirect, session, logging, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt



# მონაცემთა ბაზას ვუკავშირებთ ლოკალჰოსტს
engine = create_engine('mysql+pymysql://root:@localhost/registerr')
db=scoped_session(sessionmaker(bind=engine))



app = Flask(__name__)


# მთავარი გვერდისთვის
@app.route('/home')
def home():
    return render_template('home.html')


# კაპიტალის შეფასებისთვის
@app.route('/capital', methods=['GET', 'POST'])
def capital():
    if request.method == 'POST':
        Project = request.form['Project']
        # მოგვაქვს მონაცემები
        Bond = int(request.form['Bond'])
        Bond_rate = int(request.form['Bond_rate'])
        Tax = int(request.form['Tax'])
        
        KI = round(float(Bond_rate * (1 - (Tax/100))), 4)
        # მოგვაქვს მონაცემები
        Asset = int(request.form['Asset'])
        Asset_prise = int(request.form['Asset_prise'])
        Dividend = int(request.form['Dividend'])
        Change = int(request.form['Change'])
        
        KS = round(float(((Dividend+(Dividend*(Change/100)))/Asset_prise)*100+Change), 4)
        # მოგვაქვს მონაცემები
        Passet = int(request.form['Passet'])
        Passet_prise = int(request.form['Passet_prise'])
        P_dividend = int(request.form['P_dividend'])
        
        KD = round(float(P_dividend/Passet_prise)*100,4)

        sumcapital = round((Bond + Asset + Passet),4)
        WACC = round(float(((Bond/sumcapital)*KI)+((Asset/sumcapital)*KS) + ((Passet/sumcapital)*KD) ), 2)
        return render_template('analyse.html', Project=Project, Bond=Bond, Bond_rate=Bond_rate, Tax=Tax, KI=KI, Asset=Asset, Asset_prise=Asset_prise, Dividend=Dividend, Change=Change, KS=KS, Passet=Passet, Passet_prise=Passet_prise, P_dividend=P_dividend, KD=KD, sumcapital=sumcapital, WACC=WACC)
    return render_template('capital.html')


# კაპიტალის ანალიზისთვის 
# @app.route('/analyse', methods=['GET', 'POST'])
# def analyse():
#     return render_template('analyse.html')



# პორთფელის ანალიზისთვის
@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'POST':
        Project = request.form['Project']
        # მონაცემების წამოღება
        Risk_free = float(request.form['Risk_free'])
        MarkeT_revenue = float(request.form['MarkeT_revenue'])
        Sist_risk = float(request.form['Sist_risk'])
        Preferred_risk = float(request.form['Preferred_risk'])
        # მონაცემების დამუშავება
        Risk_market = round(float((MarkeT_revenue-Risk_free)/Sist_risk),4)
        portfolio_profit = round(float(Risk_free+((MarkeT_revenue-Risk_free)/Sist_risk)*Preferred_risk),2)

        return render_template('portfolio_analyse.html', Project=Project, Risk_free=Risk_free, MarkeT_revenue=MarkeT_revenue, Sist_risk=Sist_risk, Preferred_risk=Preferred_risk, Risk_market=Risk_market, portfolio_profit=portfolio_profit)
    
    return render_template('portfolio.html')








# რეგისტრაციის გვერდი
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # მოგვაქვს მონაცემები 
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        # პასვორდს ვუკეთებთ ენქრიპტს
        secure_password = sha256_crypt.encrypt(str(password))

        # ვამოწმებთ რეგისტრაციის პაროლი ემთხვევა თუ არა და შემდეგ ვწერთ მონაცემებთ მონაცემთა ბაზაში
        if password == confirm:
            db.execute("INSERT INTO users(name, username, password) VALUES(:name, :username, :password)", 
                        {"name":name, "username":username, "password":secure_password})
            db.commit()
            return redirect(url_for('login'))
        # თუ არ ემთხვევა ვაბრუნებთ იგივე გვერძე და ვაჩვენებთ მესიჯს
        else:
            flash('  პაროლი არ ემთხვევა  ', 'danger')
            return render_template("register.html")
            
    return render_template('register.html')



# შესვლის გვერდი
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # მოგვაქვს მონაცემები
        username = request.form.get('username')
        password = request.form.get('password')

        # ამ მონაცემებს ვადარებთ მონაცემთა ბაზის მონაცემებს
        usernamedata = db.execute('SELECT username FROM users WHERE username=:username', {"username":username}).fetchone()
        passworddata = db.execute('SELECT password FROM users WHERE username=:username', {"username":username}).fetchone()
       
        # მომხმარებელმა არასწორად შეიყვანა უზერი მაშინ დაგვიბეჭდავს მესიჯს და დაგვაბრუნებს იგივე გვერძე
        if usernamedata is None:
            flash("მომხმარებელი არ არსებობს", 'danger')
            return render_template('login.html')

        else:
            # ციკლის საშუალებით ვამოწმებთ არის თუ არა შეყვანილი პაროლი მონაცემთა ბაზაში
            for passdata in passworddata:
                # ვუკეთებთ ენქრიპთს და იმ შემთხვევაში თუ დაემთხვევა ვუშვებთ მთვარ გვერძე
                if sha256_crypt.verify(password,passdata):
                    return redirect(url_for('home'))
                # სხვა შემთხვევაში ვუგზავნით მესიჯს და ვაბრუნებთ იგივე გვერძე 
                else:
                    flash('პაროლი არ ემთხვევა', 'danger')
                    return render_template('login.html') 

    return render_template('login.html')



# secret_key უსაფრთხოების პროტოკოლისთვის
if __name__ == "__main__":
    app.secret_key="1125"
    app.run(debug=True)