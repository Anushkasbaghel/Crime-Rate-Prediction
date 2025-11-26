from flask import Flask, request, render_template
import pickle
import math
import matplotlib.pyplot as plt
import io
import base64

# Load model
model = pickle.load(open('Model/model.pkl', 'rb'))

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict_result():

    # ---------- MAPPING ----------
    city_names = {
        '0': 'Ahmedabad', '1': 'Bengaluru', '2': 'Chennai', '3': 'Coimbatore',
        '4': 'Delhi', '5': 'Ghaziabad', '6': 'Hyderabad', '7': 'Indore',
        '8': 'Jaipur', '9': 'Kanpur', '10': 'Kochi', '11': 'Kolkata',
        '12': 'Kozhikode', '13': 'Lucknow', '14': 'Mumbai', '15': 'Nagpur',
        '16': 'Patna', '17': 'Pune', '18': 'Surat'
    }

    crimes_names = {
        '0': 'Crime Committed by Juveniles', '1': 'Crime against SC', '2': 'Crime against ST',
        '3': 'Crime against Senior Citizen', '4': 'Crime against children',
        '5': 'Crime against women', '6': 'Cyber Crimes', '7': 'Economic Offences',
        '8': 'Kidnapping', '9': 'Murder'
    }

    population = {
        '0': 63.50, '1': 85.00, '2': 87.00, '3': 21.50, '4': 163.10, '5': 23.60,
        '6': 77.50, '7': 21.70, '8': 30.70, '9': 29.20, '10': 21.20, '11': 141.10,
        '12': 20.30, '13': 29.00, '14': 184.10, '15': 25.00, '16': 20.50, '17': 50.50, '18': 45.80
    }

    # ---------- READ INPUT ----------
    city_code = request.form["city"]
    crime_code = request.form["crime"]
    year = request.form["year"]
    year = int(year)

    # ---------- POPULATION CALC ----------
    pop = population[str(city_code)]

    # increase population from base year 2011
    pop = pop + (0.01 * (year - 2011) * pop)
    pop = round(pop, 3)

    # ---------- PREDICT ----------
    crime_rate = model.predict([[year, int(city_code), pop, int(crime_code)]])[0]
    crime_rate = round(crime_rate, 2)

    cases = math.ceil(crime_rate * pop)

    city_name = city_names[str(city_code)]
    crime_type = crimes_names[str(crime_code)]

    # ---------- CRIME STATUS & GLOW ----------
    if crime_rate <= 1:
        crime_status = "Very Low Crime Area"
        status_color = "#2ecc71"    # green
    elif crime_rate <= 5:
        crime_status = "Low Crime Area"
        status_color = "#f1c40f"    # yellow
    elif crime_rate <= 15:
        crime_status = "High Crime Area"
        status_color = "#e67e22"    # orange
    else:
        crime_status = "Very High Crime Area"
        status_color = "#e74c3c"    # red

    severity_width = min((crime_rate / 15) * 100, 100)

    # ======================= FUTURE TREND ===============================
    future_years = []
    future_rates = []

    for i in range(1, 6):
        fy = year + i
        future_years.append(fy)

        # population grows each year
        pop_future = pop * (1 + 0.01 * i)

        rate_future = model.predict([[fy, int(city_code), pop_future, int(crime_code)]])[0]
        future_rates.append(round(rate_future, 2))

    # ======================= CREATE TREND GRAPH =========================
    plt.figure(figsize=(5, 3))
    plt.plot(future_years, future_rates, marker='o')
    plt.title("Crime Trend for Next 5 Years")
    plt.xlabel("Year")
    plt.ylabel("Predicted Crime Rate")
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # ======================= RETURN DATA ================================
    return render_template(
        'result.html',
        city_name=city_name,
        crime_type=crime_type,
        year=year,
        crime_status=crime_status,
        crime_rate=crime_rate,
        cases=cases,
        population=pop,
        severity_width=severity_width,
        status_color=status_color,
        graph_url=graph_url
    )


if __name__ == '__main__':
    app.run(debug=False)
