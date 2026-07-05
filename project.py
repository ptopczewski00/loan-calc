import os
import openai
import tkinter as tk
from tkinter import messagebox

API_OPENAI_KEY = os.getenv("OPENAI_API_KEY")
klient = openai.OpenAI(api_key=API_OPENAI_KEY)

def interfejs():
    nazwy_pol = ["Wiek", "Staż (w obecnej pracy w latach)", "Dochód (miesięczny)", 
                "Raty (miesięczna kwota wydawana na obecne kredyty)", 
                "Kwota (kredytu jaki chcemy wziąć)", "Okres (na spłatę tego kredytu w miesiącach)"]
    slownik = {}
    inter = tk.Tk()
    inter.title("Kalkulator")
    inter.geometry("900x700")
    inter.configure(bg="#4586E8")

    tk.Label(inter, text="Dane Klienta", bg="#4586E8",font=("Arial", 14, "bold")).pack(pady=15)

    for i in nazwy_pol:
        tk.Label(inter, text=i, bg="#4586E8", fg="white", font=("Arial", 10, "bold")).pack()
        e = tk.Entry(inter, justify="center", bg="#97BBF2", fg="#081E40", font=("Arial", 10, "bold"))
        e.pack(pady=5)
        slownik[i] = e

    btn = tk.Button(inter, text="OBLICZ ZDOLNOŚĆ",bg="#CFE0FA",fg="#081E40",padx=20,pady=10,
                    command=lambda: analiza(slownik,wynik))
    
    text = tk.Label(inter, text="Wynik z analizą AI", bg="#4586E8", font=("Arial",14, "bold"))

    wynik = tk.Text(inter, height=6, wrap="word", background="#081E40",fg="white",
                    font=("Arial", 12, "bold"), padx=10, pady=10)
    
    btn.pack(pady=10)
    text.pack(pady=10)
    wynik.pack(fill="both", expand=True)
    inter.mainloop()


def analiza(pola_interfejsu, pole_wyniku):
    dane_klienta = {}
    for i in pola_interfejsu:
        dane_klienta[i] = pola_interfejsu[i].get() 
    
    if weryfikacja_danych(dane_klienta) == True:
        rata,dsti,decyzja = finanse(dane_klienta)
        wytlumaczenie = wytlumaczenie_ai(dane_klienta, decyzja, rata, dsti)
        pole_wyniku.delete("1.0", tk.END)
        pole_wyniku.insert(tk.END, f"DECYZJA: {decyzja}\n")
        pole_wyniku.insert(tk.END, f"Rata: {rata:.2f} PLN\n")
        pole_wyniku.insert(tk.END, f"DSTI: {dsti:.0%}\n\n")
        pole_wyniku.insert(tk.END, wytlumaczenie)
    else:
        messagebox.showerror("Błąd danych", "Wprowadz poprawne dane, dla Wieku: 18+, Stażu: 0.5+, Dochodu i Okresu > 0")


def weryfikacja_danych(dane):
    try:
        wiek = float(dane["Wiek"].replace(',', '.'))
        staz = float(dane["Staż (w obecnej pracy w latach)"].replace(',', '.'))
        dochod = float(dane["Dochód (miesięczny)"].replace(',', '.'))
        okres = float(dane["Okres (na spłatę tego kredytu w miesiącach)"].replace(',', '.'))

        if wiek < 18:
            return False
        elif staz < 0.5:
            return False
        elif okres <= 0:
            return False
        elif dochod <= 0:
            return False
        
        return True
    except (ValueError, KeyError):
        return False
        

def finanse(dane):
    dochod = float(dane["Dochód (miesięczny)"].replace(',', '.'))
    kwota = float(dane["Kwota (kredytu jaki chcemy wziąć)"].replace(',', '.'))
    okres = float(dane["Okres (na spłatę tego kredytu w miesiącach)"].replace(',', '.'))
    stare_raty = float(dane["Raty (miesięczna kwota wydawana na obecne kredyty)"].replace(',', '.'))
    
    rata = (kwota / okres) * 1.1
    dsti = (rata + stare_raty) / dochod
    decyzja = "TAK" if dsti < 0.5 else "NIE"
    
    return rata, dsti, decyzja


def wytlumaczenie_ai(dane,decyzja,rata,dsti):
    try:
        polecenie = f"Klient {dane['Wiek']} lat, wynik: {decyzja}, rata: {rata}, DSTI: {dsti:.0%}. Wyjaśnij decyzję w 2-3 zdaniach."
        wynik = klient.chat.completions.create(
            model = "gpt-4o-mini", 
            messages = [{"role": "user", "content": polecenie}],
            timeout=15
        )   
        return wynik.choices[0].message.content
    except:
        return "Wystąpił problem z AI"




if not API_OPENAI_KEY:
    input("nie znaleziono")
else:
    interfejs()