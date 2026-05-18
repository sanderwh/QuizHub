from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'hemmelig_nogle_til_quiz_projektet'

# Spørgsmål til quizzen
sporgsmaal = [
    {
        "sporgsmaal": "Hvad er hovedstaden i Danmark?",
        "muligheder": ["Stockholm", "Oslo", "København", "Helsinki"],
        "rigtigt_svar": "København"
    },
    {
        "sporgsmaal": "Hvad er 7 + 3?",
        "muligheder": ["9", "10", "11", "12"],
        "rigtigt_svar": "10"
    },
    {
        "sporgsmaal": "Hvilken planet er kendt som den røde planet?",
        "muligheder": ["Jupiter", "Mars", "Venus", "Saturn"],
        "rigtigt_svar": "Mars"
    },
    {
        "sporgsmaal": "Hvem skrev 'Hamlet'?",
        "muligheder": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
        "rigtigt_svar": "William Shakespeare"
    },
    {
        "sporgsmaal": "Hvad er grundstoffet for vand?",
        "muligheder": ["CO2", "O2", "H2O", "NaCl"],
        "rigtigt_svar": "H2O"
    }
]

@app.route('/')
def forside():
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        # Gem svar fra brugeren - hvert spørgsmål har sit eget navn
        svar = [
            request.form.get('q1'),
            request.form.get('q2'),
            request.form.get('q3'),
            request.form.get('q4'),
            request.form.get('q5')
        ]
        
        # Udskriv til terminal for at debugge
        print("Modtagne svar:", svar)
        
        session['bruger_svar'] = svar
        return redirect(url_for('resultat'))
    
    # GET request - vis quizzen
    return render_template('quiz.html', sporgsmaal=sporgsmaal)

@app.route('/resultat')
def resultat():
    bruger_svar = session.get('bruger_svar', [])
    
    # Hvis der ikke er nogen svar, send tilbage til quiz
    if not bruger_svar:
        return redirect(url_for('quiz'))
    
    # Beregn score
    score = 0
    resultater = []
    
    for i, spm in enumerate(sporgsmaal):
        er_rigtigt = False
        brugerens_svar = bruger_svar[i] if i < len(bruger_svar) else None
        
        # Tjek om svaret er rigtigt (og ikke None)
        if brugerens_svar and brugerens_svar == spm["rigtigt_svar"]:
            score += 1
            er_rigtigt = True
        
        # Hvis brugeren ikke har svaret
        if not brugerens_svar:
            brugerens_svar = "Intet svar valgt"
        
        resultater.append({
            "sporgsmaal": spm["sporgsmaal"],
            "dit_svar": brugerens_svar,
            "rigtigt_svar": spm["rigtigt_svar"],
            "er_rigtigt": er_rigtigt
        })
    
    total_spm = len(sporgsmaal)
    procent = (score / total_spm) * 100
    
    return render_template('result.html', 
                         score=score, 
                         total=total_spm, 
                         procent=procent,
                         resultater=resultater)

if __name__ == '__main__':
    app.run(debug=True)