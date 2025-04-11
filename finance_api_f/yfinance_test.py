import yfinance as yf
from datetime import datetime
import pandas as pd

def main():
    # Določimo simbol podjetja, za katerega želimo dobiti podatke (v tem primeru Apple)
    symbol = "AAPL"
    ticker = yf.Ticker(symbol)

    # ---------------------------------------------
    # 1. OSNOVNI PODATKI O PODJETJU: info in fast_info
    # ---------------------------------------------
    print("----- INFO (osnovni podatki o podjetju) -----")
    try:
        # info je slovar s številnimi podatki, kot so ime podjetja, sektor, opis, tržna kapitalizacija, PE razmerje, itd.
        info = ticker.info
        # Izpisemo nekaj ključnih podatkov
        print(f"Ime podjetja: {info.get('longName')}")
        print(f"Sektor: {info.get('sector')}")
        print(f"Industrija: {info.get('industry')}")
        print(f"Tržna kapitalizacija: {info.get('marketCap')}")
    except Exception as e:
        print("Napaka pri pridobivanju info:", e)
    print()

    print("----- FAST INFO (hitri osnovni podatki) -----")
    try:
        # fast_info vsebuje podatke, ki jih lahko hitro pridobiš, na primer zadnjo ceno in tržno kapitalizacijo.
        fast_info = ticker.fast_info
        print(f"Zadnja cena: {fast_info.get('last_price')}")
        print(f"Tržna kapitalizacija (hitro): {fast_info.get('market_cap')}")
    except Exception as e:
        print("Napaka pri pridobivanju fast_info:", e)
    print()

    # ---------------------------------------------
    # 2. ZGODOVINSKI PODATKI: history
    # ---------------------------------------------
    print("----- ZGODOVINSKI PODATKI (zadnji mesec) -----")
    try:
        # Pridobitev zgodovinskih podatkov za zadnji mesec. Rezultat je pandas DataFrame.
        hist = ticker.history(period="1mo")
        print(hist)
    except Exception as e:
        print("Napaka pri pridobivanju zgodovinskih podatkov:", e)
    print()

    # ---------------------------------------------
    # 3. DIVIDENDE IN DELITVE
    # ---------------------------------------------
    print("----- DIVIDENDE -----")
    try:
        # Pridobimo podatke o dividendah; vrne pandas Series, kjer so datumi in zneski dividend.
        dividends = ticker.dividends
        print(dividends)
    except Exception as e:
        print("Napaka pri pridobivanju dividend:", e)
    print()

    print("----- DELITVE (splits) -----")
    try:
        # Pridobimo podatke o delitvah delnic, če so bile izvedene.
        splits = ticker.splits
        print(splits)
    except Exception as e:
        print("Napaka pri pridobivanju delitev:", e)
    print()

    # ---------------------------------------------
    # 4. FINANČNA POROČILA: income statement, balance sheet, cashflow
    # ---------------------------------------------
    print("----- FINANČNA POROČILA: Izkaz poslovnega izida -----")
    try:
        # Prikaže izkaz poslovnega izida (income statement) kot pandas DataFrame.
        financials = ticker.financials
        print(financials)
    except Exception as e:
        print("Napaka pri pridobivanju finančnih poročil:", e)
    print()

    print("----- BALANČNI LIST (balance sheet) -----")
    try:
        # Bilanca stanja, ki prikazuje sredstva in obveznosti podjetja.
        balance_sheet = ticker.balance_sheet
        print(balance_sheet)
    except Exception as e:
        print("Napaka pri pridobivanju bilance stanja:", e)
    print()

    print("----- DENARNI TOK (cashflow) -----")
    try:
        # Prikaz denarnega toka podjetja.
        cashflow = ticker.cashflow
        print(cashflow)
    except Exception as e:
        print("Napaka pri pridobivanju denarnega toka:", e)
    print()

    # ---------------------------------------------
    # 5. KOLEDAR DOGODKOV: calendar
    # ---------------------------------------------
    print("----- KOLEDAR DOGODKOV (npr. objava rezultatov) -----")
    try:
        # Prikaz prihodnjih pomembnih dogodkov, kot so datumi objav rezultatov.
        calendar = ticker.calendar
        print(calendar)
    except Exception as e:
        print("Napaka pri pridobivanju koledarja dogodkov:", e)
    print()

    # ---------------------------------------------
    # 6. TRAJNOST IN ESG: sustainability
    # ---------------------------------------------
    print("----- TRAJNOST / ESG (okoljski, socialni in upravljalski kazalniki) -----")
    try:
        # Pridobi podatke o trajnostnih kazalnikih, če so na voljo.
        sustainability = ticker.sustainability
        print(sustainability)
    except Exception as e:
        print("Napaka pri pridobivanju trajnostnih kazalnikov:", e)
    print()

    # ---------------------------------------------
    # 7. PODATKI O LASTNIŠTVU: major, institucionalni in vzajemni skladi
    # ---------------------------------------------
    print("----- GLAVNI DELNIČARJI (major holders) -----")
    try:
        major_holders = ticker.major_holders
        print(major_holders)
    except Exception as e:
        print("Napaka pri pridobivanju glavnih delničarjev:", e)
    print()

    print("----- INSTITUCIONALNI DELNIČARJI -----")
    try:
        inst_holders = ticker.institutional_holders
        print(inst_holders)
    except Exception as e:
        print("Napaka pri pridobivanju institucionalnih delničarjev:", e)
    print()

    print("----- VZAJEMNI SKLADI (mutualfund holders) -----")
    try:
        mf_holders = ticker.mutualfund_holders
        print(mf_holders)
    except Exception as e:
        print("Napaka pri pridobivanju vzajemnih skladov:", e)
    print()

    # ---------------------------------------------
    # 8. PRIPOROČILA ANALITIKOV: recommendations
    # ---------------------------------------------
    print("----- PRIPOROČILA ANALITIKOV -----")
    try:
        recommendations = ticker.recommendations
        print(recommendations)
    except Exception as e:
        print("Napaka pri pridobivanju priporočil analitikov:", e)
    print()

    # ---------------------------------------------
    # 9. DOBIČKI: earnings in earnings trend
    # ---------------------------------------------
    print("----- DOBIČKI (earnings) -----")
    try:
        income_stmt = ticker.income_stmt
        print(income_stmt)
    except Exception as e:
        print("Napaka pri pridobivanju dobičkov:", e)
    print()

    print("----- TRENDO DOBIČKOV (earnings trend) -----")
    try:
        earnings_trend = ticker.earnings_trend
        print(earnings_trend)
    except Exception as e:
        print("Napaka pri pridobivanju trendov dobičkov:", e)
    print()

    # ---------------------------------------------
    # 10. OPCIJE: options in option_chain
    # ---------------------------------------------
    print("----- OPCIJE (seznam datumov poteka opcij) -----")
    try:
        options = ticker.options
        print(options)
    except Exception as e:
        print("Napaka pri pridobivanju opcij:", e)
    print()

    if options:
        # Če obstajajo možnosti, vzamemo prvi datum poteka in prikažemo verigo opcij
        expiry = options[0]
        print(f"----- OPCIJSKA VERIGA za datum {expiry} -----")
        try:
            opt_chain = ticker.option_chain(expiry)
            print("Calls:")
            print(opt_chain.calls)
            print("Puts:")
            print(opt_chain.puts)
        except Exception as e:
            print("Napaka pri pridobivanju opcijske verige:", e)
    print()


if __name__ == "__main__":
    main()
