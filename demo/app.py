# ============================================
# IMPORTERING AF NØDVENDIGE MODULER
# ============================================

from flask import Flask, render_template, request, session, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'hemmelig_nogle'

# ============================================
# ADMIN KONFIGURATION
# ============================================

# Admin login (I kan ændre brugernavn og kodeord her)
ADMIN_BRUGER = "admin"
ADMIN_KODEORD = "hemmelig123"

# Opret quizzes mappe hvis den ikke findes
if not os.path.exists('quizzes'):
    os.makedirs('quizzes')


# ============================================
# HJÆLPEFUNKTIONER TIL JSON
# ============================================

def hent_alle_quizzes():
    """Henter navnene på alle quizzes fra quizzes mappen."""
    quizzes = []
    
    if not os.path.exists('quizzes'):
        return quizzes
    
    for filnavn in os.listdir('quizzes'):
        if filnavn.endswith('.json'):
            fil_sti = os.path.join('quizzes', filnavn)
            try:
                with open(fil_sti, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    quizzes.append({
                        'navn': data.get('navn', filnavn.replace('.json', '')),
                        'filnavn': filnavn,
                        'beskrivelse': data.get('beskrivelse', 'Ingen beskrivelse')
                    })
            except:
                pass
    
    return quizzes


def hent_quiz(filnavn):
    """Henter en specifik quiz fra en JSON fil."""
    fil_sti = os.path.join('quizzes', filnavn)
    
    if not os.path.exists(fil_sti):
        return None
    
    with open(fil_sti, 'r', encoding='utf-8') as f:
        quiz_data = json.load(f)
    
    return quiz_data


def gem_quiz(quiz_data, filnavn):
    """Gemmer en ny quiz som en JSON fil."""
    fil_sti = os.path.join('quizzes', filnavn)
    
    with open(fil_sti, 'w', encoding='utf-8') as f:
        json.dump(quiz_data, f, indent=4, ensure_ascii=False)


def slet_quiz(filnavn):
    """Sletter en quiz fil."""
    fil_sti = os.path.join('quizzes', filnavn)
    
    if os.path.exists(fil_sti):
        os.remove(fil_sti)
        return True
    return False


# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login side"""
    if request.method == 'POST':
        bruger = request.form.get('bruger')
        kodeord = request.form.get('kodeord')
        
        if bruger == ADMIN_BRUGER and kodeord == ADMIN_KODEORD:
            session['admin_logget_ind'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', fejl="Forkert brugernavn eller kodeord!")
    
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logget_ind', None)
    return redirect(url_for('forside'))


@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard - viser alle quizzes med slet knapper"""
    # Tjek om admin er logget ind
    if not session.get('admin_logget_ind'):
        return redirect(url_for('admin_login'))
    
    alle_quizzes = hent_alle_quizzes()
    return render_template('admin_dashboard.html', quizzes=alle_quizzes)


@app.route('/admin/slet/<filnavn>')
def admin_slet(filnavn):
    """Sletter en quiz"""
    # Tjek om admin er logget ind
    if not session.get('admin_logget_ind'):
        return redirect(url_for('admin_login'))
    
    slet_quiz(filnavn)
    return redirect(url_for('admin_dashboard'))


# ============================================
# ORDINÆRE ROUTES
# ============================================

@app.route('/')
def forside():
    alle_quizzes = hent_alle_quizzes()
    admin_logget_ind = session.get('admin_logget_ind', False)
    return render_template('index.html', quizzes=alle_quizzes, admin_logget_ind=admin_logget_ind)


@app.route('/select_quiz')
def select_quiz():
    alle_quizzes = hent_alle_quizzes()
    return render_template('select_quiz.html', quizzes=alle_quizzes)


@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        quiz_navn = request.form.get('quiz_navn')
        antal_spm = int(request.form.get('antal_spm', 3))
        
        sporgsmaal_liste = []
        for i in range(antal_spm):
            spm_tekst = request.form.get(f'sp_{i}')
            mulighed1 = request.form.get(f'mul_{i}_0')
            mulighed2 = request.form.get(f'mul_{i}_1')
            mulighed3 = request.form.get(f'mul_{i}_2')
            mulighed4 = request.form.get(f'mul_{i}_3')
            rigtigt_svar = request.form.get(f'rigtigt_{i}')
            
            sporgsmaal_liste.append({
                "sporgsmaal": spm_tekst,
                "muligheder": [mulighed1, mulighed2, mulighed3, mulighed4],
                "rigtigt_svar": rigtigt_svar
            })
        
        filnavn = quiz_navn.lower().replace(' ', '_').replace('æ', 'ae').replace('ø', 'oe').replace('å', 'aa') + '.json'
        
        ny_quiz = {
            "navn": quiz_navn,
            "beskrivelse": request.form.get('beskrivelse', 'En brugeroprettet quiz'),
            "sporgsmaal": sporgsmaal_liste
        }
        
        gem_quiz(ny_quiz, filnavn)
        return redirect(url_for('select_quiz'))
    
    return render_template('create_quiz.html')


@app.route('/quiz/<filnavn>', methods=['GET', 'POST'])
def quiz(filnavn):
    quiz_data = hent_quiz(filnavn)
    
    if quiz_data is None:
        return "Quiz ikke fundet!", 404
    
    sporgsmaal = quiz_data['sporgsmaal']
    quiz_navn = quiz_data['navn']
    
    if request.method == 'POST':
        svar = []
        for i in range(len(sporgsmaal)):
            svar_værdi = request.form.get(f'q{i}')
            svar.append(svar_værdi)
        
        session['bruger_svar'] = svar
        session['quiz_filnavn'] = filnavn
        session['quiz_navn'] = quiz_navn
        
        return redirect(url_for('resultat'))
    
    return render_template('quiz.html', sporgsmaal=sporgsmaal, quiz_navn=quiz_navn, filnavn=filnavn)


@app.route('/resultat')
def resultat():
    bruger_svar = session.get('bruger_svar', [])
    filnavn = session.get('quiz_filnavn')
    
    quiz_data = hent_quiz(filnavn)
    if quiz_data is None:
        return "Quiz ikke fundet!", 404
    
    sporgsmaal = quiz_data['sporgsmaal']
    quiz_navn = quiz_data.get('navn', 'Quiz')
    
    score = 0
    resultater = []
    
    for i, spm in enumerate(sporgsmaal):
        er_rigtigt = False
        brugerens_svar = bruger_svar[i] if i < len(bruger_svar) else "Intet svar"
        
        if brugerens_svar == spm["rigtigt_svar"]:
            score += 1
            er_rigtigt = True
        
        resultater.append({
            "sporgsmaal": spm["sporgsmaal"],
            "dit_svar": brugerens_svar,
            "rigtigt_svar": spm["rigtigt_svar"],
            "er_rigtigt": er_rigtigt
        })
    
    total = len(sporgsmaal)
    procent = (score / total) * 100 if total > 0 else 0
    
    return render_template('result.html', 
                         score=score, 
                         total=total, 
                         procent=procent,
                         quiz_navn=quiz_navn,
                         resultater=resultater)


# ============================================
# START AF SERVEREN
# ============================================

if __name__ == '__main__':
    app.run(debug=True)